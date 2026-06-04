+++
title       = "Kubernetes लोड बॅलेन्सर: आत, बाहेर, की दोन्ही?"
description = "ClusterIP पासून Gateway API पर्यंत — प्रत्येक Kubernetes लोड बॅलेन्सर पर्याय समजावून सांगितला आहे. तुमच्या सेटअपसाठी क्लस्टरच्या आत की बाहेर काय योग्य आहे ते जाणून घ्या."
date        = "2026-06-04T15:30:08+05:30"
slug          = "kubernetes-load-balancer-options"
tags          = ["kubernetes", "devops", "networking"]
keywords      = ["Kubernetes load balancer", "k8s load balancing", "MetalLB", "Kubernetes Ingress", "Gateway API", "EKS load balancer"]
canonical     = "/mr/posts/kubernetes-load-balancer-options/"
feature_image = "https://images.unsplash.com/photo-1558494949-ef010cbdcc31?w=1200"
+++

Kubernetes क्लस्टर सेट करणारा प्रत्येक जण शेवटी एकाच अडथळ्यावर येतो: या सिस्टममध्ये ट्राफिक नेमका कसा आणायचा? मग डॉक्युमेंटेशन ClusterIP, NodePort, LoadBalancer, Ingress, Gateway API, MetalLB — असे उल्लेख करतं आणि गोंधळ वाढत जातो. आणखी एक समस्या म्हणजे "LoadBalancer" नावाचा एक Service *type* आहे आणि प्रत्यक्ष लोड बॅलेन्सर आहेत — आणि ते एकच नाहीत. चला खऱ्या पर्यायांतून जाऊया, स्टॅकमध्ये प्रत्येक कुठे बसतो, आणि खरोखरच काय वापरणे योग्य आहे ते पाहूया.

## दोन प्रकारचा ट्राफिक

कोणताही लोड बॅलेन्सर मेकॅनिझम निवडण्याआधी, तुम्ही नेमकी कोणती समस्या सोडवत आहात हे जाणून घेणे उपयुक्त आहे.

**East-west ट्राफिक** म्हणजे क्लस्टरच्या आतील pod-to-pod संवाद — तुमची auth service तुमच्या user service ला कॉल करत आहे. Kubernetes हे नेटिव्हली हाताळतो. प्रत्येक `Service` ला एक स्थिर व्हर्च्युअल IP आणि DNS नाव मिळतो, आणि प्रत्येक नोडवर चालणारा `kube-proxy` healthy pods वर पॅकेट्स round-robin करण्यासाठी `iptables` (किंवा मोठ्या क्लस्टर्समध्ये IPVS) प्रोग्राम करतो [1]. East-west ट्राफिकसाठी तुम्हाला बाह्य लोड बॅलेन्सरची अजिबात गरज नाही.

**North-south ट्राफिक** म्हणजे इंटरनेटवरून बाह्य क्लायंट्स तुमच्या अॅपवर पोहोचत आहेत. Kubernetes जाणूनबुजून बाह्य नेटवर्किंग लेयर स्वतः प्रोव्हिजन करत नाही — ते cloud provider इंटिग्रेशन किंवा तुम्ही जे काही जोडता त्याकडे सोपवतो [1]. खाली दिलेले सर्व पर्याय इथेच येतात.

## पाच पर्याय

एकच योग्य उत्तर नाही. प्रत्येक मेकॅनिझम समस्येच्या वेगळ्या लेयरला लक्ष्य करतो.

| पर्याय | OSI लेयर | बाह्य IP मिळतो? | सर्वोत्तम कशासाठी |
|---|---|---|---|
| ClusterIP | L4 (अंतर्गत) | नाही | क्लस्टरच्या आतील Pod-to-pod |
| NodePort | L4 | नोड IP द्वारे (hack) | फक्त लोकल dev आणि झटपट चाचण्या |
| Service type LoadBalancer | L4 | होय — प्रत्येक Service साठी एक | थोड्या महत्त्वाच्या Services साठी |
| Ingress + Controller | L7 (HTTP/HTTPS) | शेअर्ड, सर्वांसाठी एक | अनेक HTTP services, एकच IP |
| Gateway API | L4 + L7 | शेअर्ड | नवीन क्लस्टर्स, Ingress ची जागा घेतो |

### ClusterIP

डिफॉल्ट Service type [1]. एक cluster-internal व्हर्च्युअल IP नियुक्त करतो जो फक्त क्लस्टरच्या आतील pods पोहोचू शकतात. एकमेकांशी बोलणाऱ्या microservices साठी हे सर्व जे तुम्हाला हवे आहे ते आहे. **बाह्यरित्या काहीतरी expose करण्याचे ठोस कारण नसल्यास ClusterIP डिफॉल्ट ठेवा.** वास्तविक क्लस्टरमधील बहुतेक services ला बाह्य IP ची गरज नाही — त्यांना फक्त इतर services ला त्यांना शोधता येणे आवश्यक आहे.

### NodePort

प्रत्येक नोडवर `30000–32767` श्रेणीतील एक port उघडतो [2]. कोणत्याही नोडवर त्या port वर येणारा ट्राफिक Service ला फॉरवर्ड केला जातो. तांत्रिकदृष्ट्या बाह्य क्लायंट्सपर्यंत पोहोचतो पण हे एक hack आहे — तुम्ही non-standard ports expose करत आहात, बदलणाऱ्या नोड IPs वर अवलंबून आहात, आणि कोणत्याही वास्तविक infrastructure-level load balancing ला bypass करत आहात. मी `kind` किंवा `minikube` वर काहीतरी काम करतेय का हे झटपट तपासण्यासाठी NodePort वापरला आहे. Production मध्ये कधीही नाही.

### Service type LoadBalancer

जेव्हा तुम्ही Service वर `type: LoadBalancer` सेट करता, तेव्हा Kubernetes अंतर्निहित cloud provider ला एक वास्तविक लोड बॅलेन्सर प्रोव्हिजन करण्यास आणि बाह्य IP नियुक्त करण्यास सांगतो [1][3]. AWS वर तुम्हाला NLB किंवा ALB मिळतो (annotations वर अवलंबून), GCP वर एक regional TCP/UDP लोड बॅलेन्सर, Azure वर Azure LB सह एक public IP.

समस्या: **प्रत्येक `LoadBalancer` Service स्वतःचा वेगळा cloud लोड बॅलेन्सर प्रोव्हिजन करतो.** 20-service अॅप्लिकेशनवर ते 20 provisioned लोड बॅलेन्सर आणि 20 बाह्य IPs आहेत. खर्च झटपट वाढतो, आणि operational overhead वास्तविक आहे [3]. तुम्हाला खरोखरच एक dedicated बाह्य endpoint आवश्यक असलेल्या थोड्या services साठी हा type वापरा. क्लस्टरमधील प्रत्येक service साठी डिफॉल्ट pattern म्हणून नाही.

### Ingress + Controller

बहुतेक teams HTTP workloads साठी इथेच पोहोचतात. एक `Ingress` resource routing नियम परिभाषित करतो — `/api/*` service-a कडे route करा, `/web/*` service-b कडे route करा — आणि एक Ingress Controller (nginx, Traefik, HAProxy, इ.) ते क्लस्टरच्या आत implement करतो [3].

तुम्हाला अजूनही Ingress Controller च्या समोर नेमका *एक* बाह्य लोड बॅलेन्सर हवा आहे, पण मग तुमचे सर्व HTTP/HTTPS routing एकाच बाह्य IP मागे क्लस्टरच्या आत होते. TLS termination controller वर होते. Service दर लोड बॅलेन्सरपेक्षा खूपच स्वस्त.

तथापि दोन खऱ्या मर्यादा आहेत. पहिली, **Ingress फक्त HTTP साठी आहे.** TCP/UDP routing साठी बहुतेक controllers ला custom annotations आवश्यक आहेत, जे vendor-specific आहेत आणि portable नाहीत [4]. दुसरी, Kubernetes project ने Ingress API गोठवली आहे. कोणत्याही नवीन features जोडल्या जात नाहीत [5]. हे अजूनही विद्यमान setups साठी ठीक काम करते, पण नवीन features Gateway API मध्ये जात आहेत.

### Gateway API

Gateway API हा Ingress चा योग्य उत्तराधिकारी आहे, 2026 पर्यंत Layer 4 आणि Layer 7 दोन्हीसाठी GA आहे [4][5]. हे मुख्य निराशा दूर करते:

- **नेटिव्ह TCP, UDP, आणि gRPC समर्थन** — फक्त HTTP/HTTPS नाही
- **भूमिका-केंद्रित design** — cluster operators `Gateway` resource (infrastructure) चे मालक आहेत; app developers `HTTPRoute` किंवा `TCPRoute` (routing नियम) चे मालक आहेत. वेगळ्या objects, वेगळ्या RBAC. आता समन्वयाचे भयस्वप्न नाही [4]
- **Portable** — spec implementations मध्ये सुसंगत आहे: Envoy Gateway, Istio, NGINX, Cilium, Kong, Traefik. आता vendor-specific annotations नाही [4]

जर तुम्ही आज एक नवीन क्लस्टर सुरू करत असाल, तर Gateway API वापरा. प्रमुख cloud providers ते थेट support करतात. Ingress वर्षानुवर्षे काम करेल पण ते फक्त technical debt जमा करत आहे [5].

## Bare Metal बद्दल काय?

Cloud providers तुमच्यासाठी `LoadBalancer` Service plumbing पारदर्शकपणे जोडतात. Bare metal वर — self-managed VMs, एक on-prem rack, k3s चालवणारी home lab — कोणताही cloud provider नाही. तुमच्या `type: LoadBalancer` Services अनिश्चित काळासाठी `<pending>` स्थितीत राहतील [6].

**MetalLB** हा मानक उपाय आहे. हे तुमच्या क्लस्टरला स्वतःचा IP pool देतो आणि ते IPs Layer 2 (ARP) किंवा BGP द्वारे advertise करतो [7]. तुम्ही तुमच्या local network वर IPs ची श्रेणी वेगळी करता, MetalLB ला `IPAddressPool` सह configure करता, आणि ते LoadBalancer Services साठी IP नियुक्ती ताब्यात घेते.

सामान्य bare-metal stack:

1. MetalLB तुमच्या pool मधून Ingress Controller च्या Service ला एक IP नियुक्त करतो
2. Ingress Controller (nginx-ingress, Traefik) HTTP routing आणि TLS हाताळतो
3. अंतर्गत services ClusterIP वर राहतात

```yaml
# MetalLB साठी IPs राखून ठेवा — नोड IPs किंवा DHCP-managed addresses पुन्हा वापरू नका
apiVersion: metallb.io/v1beta1
kind: IPAddressPool
metadata:
  name: local-pool
  namespace: metallb-system
spec:
  addresses:
  - 192.168.1.200-192.168.1.210
---
apiVersion: metallb.io/v1beta1
kind: L2Advertisement
metadata:
  name: default
  namespace: metallb-system
```

MetalLB failover देखील हाताळतो — जर IP advertise करणारा नोड बंद पडला, तर ते दुसऱ्या नोडवरून पुन्हा advertise करतो. IP क्लायंट्ससाठी स्थिर राहतो [7].

## Cloud क्लस्टर्स: AWS EKS उदाहरण

EKS वर, तुम्ही **AWS Load Balancer Controller** install करता जे Kubernetes Service आणि Ingress objects ला वास्तविक AWS resources मध्ये reconcile करतो [8]. Mapping सरळ आहे:

| K8s Object | AWS Resource | काय करतो |
|---|---|---|
| `Service` (type LoadBalancer) | AWS Network Load Balancer (NLB) | L4, static IP, TCP/UDP |
| `Ingress` | AWS Application Load Balancer (ALB) | L7, WAF, Cognito, path routing |
| `HTTPRoute` (Gateway API) | ALB via Gateway API controller | L7, आधुनिक declarative config |

एक गोष्ट जी मला त्रास देली: **विद्यमान Service वर `service.beta.kubernetes.io/aws-load-balancer-type` annotation कधीही बदलू नका.** जर तुम्हाला ते बदलण्याची गरज असेल, तर Service delete करा आणि पुन्हा तयार करा. In place बदल केल्यास leaked AWS resources होतात जे साफ केले जात नाहीत [8].

EKS Auto Mode आता `LoadBalancer` Service तयार करताना NLB provisioning आपोआप हाताळतो — कोणतीही अतिरिक्त controller installation आवश्यक नाही [8]. मूलभूत NLB गरजांपलीकडे कोणत्याही गोष्टीसाठी, Load Balancer Controller अजूनही योग्य साधन आहे.

## आत की बाहेर? दोन्ही.

प्रश्न स्वतःच थोडा खोटा पर्याय आहे. **Production Kubernetes load balancing नेहमी layered असते**, pick-one निर्णय नाही:

- **क्लस्टरच्या बाहेर** — एक cloud LB किंवा MetalLB स्थिर बाह्य endpoint प्रदान करतो आणि raw L4 ट्राफिक हाताळतो
- **क्लस्टरच्या काठावर (आत)** — एक Ingress Controller किंवा Gateway API HTTP routing, TLS termination, rate limiting, आणि path-based नियम हाताळतो
- **आत अधिक खोलवर** — ClusterIP Services pods मधील सर्व east-west ट्राफिक हाताळतात, बाहेरील कोणत्याही गोष्टीला अदृश्य

![k8s load balancer architecture](/images/posts/kubernetes-load-balancer-options/k8s-load-balancer-architecture.svg)

हे सर्व एका मेकॅनिझममध्ये संकुचित करण्याचा प्रयत्न नेहमीच त्रास देतो. Service दर एक बाह्य LB महाग आहे. Cloud NLB वर थेट complex L7 routing करण्याचा प्रयत्न अवघड आहे. Ingress Controller ला तुमचा L4 TCP router म्हणून वागवण्यासाठी hacks आवश्यक आहेत. Layers एका कारणासाठी अस्तित्वात आहेत.

NodePort खरोखरच फक्त local dev किंवा CI environments साठी आहे. जर कोणी तुम्हाला "सोपे ठेवण्यासाठी production मध्ये फक्त NodePort वापरा" असे सांगितले — तर विरोध करा. तुम्ही infrastructure-level load balancing bypass करत आहात, स्वतःला नोड IPs ला lock करत आहात, आणि non-standard firewall ports उघडत आहात. पहिल्या आठवड्यानंतर हे खरोखरच काहीही सोपे करत नाही.

> समाप्त

## स्रोत
1. [Services, Load Balancing, आणि Networking | Kubernetes](https://kubernetes.io/docs/concepts/services-networking/)
2. [Kubernetes Load Balancer: पर्याय काय आहेत? | Komodor](https://komodor.com/learn/kubernetes-load-balancer-what-are-the-options/)
3. [Kubernetes Services, LoadBalancers, आणि Ingress चा अंतिम मार्गदर्शक | Robusta](https://home.robusta.dev/blog/kubernetes-service-vs-loadbalancer-vs-ingress)
4. [Kubernetes Gateway API समजून घेणे: Traffic Management साठी एक आधुनिक दृष्टिकोन | CNCF](https://www.cncf.io/blog/2025/05/02/understanding-kubernetes-gateway-api-a-modern-approach-to-traffic-management/)
5. [Gateway API | Kubernetes](https://kubernetes.io/docs/concepts/services-networking/gateway/)
6. [Bare-metal विचार - Ingress-Nginx Controller](https://kubernetes.github.io/ingress-nginx/deploy/baremetal/)
7. [Nginx Ingress Controller सह MetalLB कसे Deploy करावे | OneUptime](https://oneuptime.com/blog/post/2026-02-20-metallb-nginx-ingress/view)
8. [Load Balancing - Amazon EKS Best Practices](https://docs.aws.amazon.com/eks/latest/best-practices/load-balancing.html)