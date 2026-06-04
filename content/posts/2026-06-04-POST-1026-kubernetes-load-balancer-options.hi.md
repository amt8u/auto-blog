+++
title       = "Kubernetes लोड बैलेंसर: अंदर, बाहर, या दोनों?"
description = "हर Kubernetes लोड बैलेंसर विकल्प की व्याख्या — ClusterIP से Gateway API तक। जानें कि आपके सेटअप के लिए क्लस्टर के अंदर या बाहर क्या सही है।"
date        = "2026-06-04T15:30:08+05:30"
slug          = "kubernetes-load-balancer-options"
tags          = ["kubernetes", "devops", "नेटवर्किंग"]
keywords      = ["Kubernetes लोड बैलेंसर", "k8s लोड बैलेंसिंग", "MetalLB", "Kubernetes Ingress", "Gateway API", "EKS लोड बैलेंसर"]
canonical     = "/hi/posts/kubernetes-load-balancer-options/"
feature_image = "https://images.unsplash.com/photo-1558494949-ef010cbdcc31?w=1200"
+++

Kubernetes क्लस्टर सेटअप करने वाला हर कोई अंततः एक ही दीवार से टकराता है: मैं इस चीज़ में ट्रैफ़िक कैसे लाऊं? फिर डॉक्स में ClusterIP, NodePort, LoadBalancer, Ingress, Gateway API, MetalLB का जिक्र होता है — और मामला उलझता जाता है। इससे भी बुरी बात यह है कि Service का एक *type* "LoadBalancer" है और असली लोड बैलेंसर भी हैं, और ये दोनों एक ही चीज़ नहीं हैं। मैं वास्तविक विकल्पों के बारे में बताऊंगा, हर एक स्टैक में कहाँ बैठता है, और किस स्थिति में किसका उपयोग करना वाकई समझदारी है।

## दो तरह का ट्रैफ़िक

कोई भी लोड बैलेंसर तंत्र चुनने से पहले यह जानना जरूरी है कि आप असल में कौन सी समस्या हल कर रहे हैं।

**ईस्ट-वेस्ट ट्रैफ़िक** क्लस्टर के अंदर पॉड-से-पॉड संचार है — जैसे आपकी auth service आपकी user service को कॉल कर रही हो। Kubernetes इसे नेटिव रूप से संभालता है। हर `Service` को एक स्थिर वर्चुअल IP और एक DNS नाम मिलता है, और हर नोड पर चलने वाला `kube-proxy` स्वस्थ पॉड्स में पैकेट राउंड-रॉबिन करने के लिए `iptables` (या बड़े क्लस्टर में IPVS) को प्रोग्राम करता है [1]। ईस्ट-वेस्ट ट्रैफ़िक के लिए आपको बाहरी लोड बैलेंसर की बिल्कुल जरूरत नहीं है।

**नॉर्थ-साउथ ट्रैफ़िक** इंटरनेट से बाहरी क्लाइंट का आपके ऐप तक पहुंचना है। Kubernetes जानबूझकर बाहरी नेटवर्किंग लेयर खुद प्रोविज़न नहीं करता — वह इसे क्लाउड प्रोवाइडर इंटीग्रेशन या जो भी आप प्लग इन करते हैं उसे सौंप देता है [1]। यहीं पर नीचे दिए सभी विकल्प काम आते हैं।

## पाँच विकल्प

कोई एक सही जवाब नहीं है। हर तंत्र समस्या की एक अलग लेयर को लक्षित करता है।

| विकल्प | OSI लेयर | बाहरी IP मिलता है? | सबसे उपयुक्त |
|---|---|---|---|
| ClusterIP | L4 (आंतरिक) | नहीं | क्लस्टर के अंदर पॉड-से-पॉड |
| NodePort | L4 | नोड IP के ज़रिए (हैक) | केवल लोकल डेव और त्वरित परीक्षण |
| Service type LoadBalancer | L4 | हाँ — प्रति Service एक | थोड़े महत्वपूर्ण Services के लिए |
| Ingress + Controller | L7 (HTTP/HTTPS) | साझा, सभी के लिए एक | एकाधिक HTTP सेवाएं, एकल IP |
| Gateway API | L4 + L7 | साझा | नए क्लस्टर, Ingress की जगह |

### ClusterIP

डिफ़ॉल्ट Service type [1]। एक क्लस्टर-आंतरिक वर्चुअल IP असाइन करता है जिसे केवल क्लस्टर के अंदर के पॉड ही पहुंच सकते हैं। माइक्रोसेवाएं आपस में बात करने के लिए यही काफी है। **जब तक कुछ बाहरी रूप से एक्सपोज़ करने का ठोस कारण न हो, ClusterIP को डिफ़ॉल्ट रखें।** वास्तविक क्लस्टर की अधिकांश सेवाओं को बाहरी IP की ज़रूरत नहीं होती — उन्हें बस यह चाहिए कि दूसरी सेवाएं उन्हें ढूंढ सकें।

### NodePort

हर नोड पर `30000–32767` रेंज में एक पोर्ट खोलता है [2]। किसी भी नोड पर उस पोर्ट पर आने वाला ट्रैफ़िक Service को फॉरवर्ड हो जाता है। तकनीकी रूप से बाहरी क्लाइंट तक पहुंचता है लेकिन यह एक हैक है — आप नॉन-स्टैंडर्ड पोर्ट एक्सपोज़ कर रहे हैं, बदलने वाले नोड IPs पर निर्भर हैं, और किसी भी असली इन्फ्रास्ट्रक्चर-स्तरीय लोड बैलेंसिंग को बायपास कर रहे हैं। मैंने `kind` या `minikube` पर NodePort का उपयोग किया है ताकि जल्दी जांच सकूं कि कुछ काम करता है या नहीं। प्रोडक्शन में कभी नहीं।

### Service type LoadBalancer

जब आप किसी Service पर `type: LoadBalancer` सेट करते हैं, तो Kubernetes अंतर्निहित क्लाउड प्रोवाइडर से वास्तविक लोड बैलेंसर प्रोविज़न करने और बाहरी IP असाइन करने के लिए कहता है [1][3]। AWS पर आपको NLB या ALB (annotations पर निर्भर) मिलता है, GCP पर एक रीजनल TCP/UDP लोड बैलेंसर, Azure पर एक Azure LB के साथ पब्लिक IP।

समस्या यह है: **हर `LoadBalancer` Service अपना अलग क्लाउड लोड बैलेंसर प्रोविज़न करती है।** 20-सेवा वाले एप्लिकेशन पर वह 20 प्रोविज़न किए गए लोड बैलेंसर और 20 बाहरी IPs हैं। लागत जल्दी बढ़ती है, और ऑपरेशनल ओवरहेड वास्तविक है [3]। इस type का उपयोग उन थोड़ी सी सेवाओं के लिए करें जहाँ आपको वाकई एक समर्पित बाहरी endpoint चाहिए। क्लस्टर की हर सेवा के लिए डिफ़ॉल्ट पैटर्न के रूप में नहीं।

### Ingress + Controller

HTTP वर्कलोड के लिए अधिकांश टीमें यहीं पहुंचती हैं। एक `Ingress` resource रूटिंग नियम परिभाषित करता है — `/api/*` को service-a पर रूट करो, `/web/*` को service-b पर रूट करो — और एक Ingress Controller (nginx, Traefik, HAProxy, आदि) उन्हें क्लस्टर के अंदर लागू करता है [3]।

Ingress Controller के सामने आपको अभी भी ठीक *एक* बाहरी लोड बैलेंसर चाहिए, लेकिन फिर आपकी सारी HTTP/HTTPS रूटिंग एकल बाहरी IP के पीछे क्लस्टर के अंदर होती है। TLS termination controller पर होती है। प्रति सेवा एक लोड बैलेंसर से बहुत सस्ता।

हालांकि दो वास्तविक सीमाएं हैं। पहली, **Ingress केवल HTTP के लिए है।** TCP/UDP रूटिंग के लिए अधिकांश controllers को कस्टम annotations चाहिए, जो vendor-specific हैं और portable नहीं [4]। दूसरी, Kubernetes प्रोजेक्ट ने Ingress API को फ्रीज़ कर दिया है। कोई नई सुविधाएं नहीं जोड़ी जा रही [5]। मौजूदा सेटअप के लिए यह ठीक काम करता है, लेकिन नई सुविधाएं Gateway API में जा रही हैं।

### Gateway API

Gateway API, Ingress का उचित उत्तराधिकारी है, जो 2026 तक Layer 4 और Layer 7 दोनों के लिए GA हो चुका है [4][5]। यह मुख्य कमियों को दूर करता है:

- **नेटिव TCP, UDP, और gRPC सपोर्ट** — केवल HTTP/HTTPS नहीं
- **रोल-ओरिएंटेड डिज़ाइन** — क्लस्टर ऑपरेटर `Gateway` resource के मालिक हैं (इन्फ्रास्ट्रक्चर); ऐप डेवलपर `HTTPRoute` या `TCPRoute` के मालिक हैं (रूटिंग नियम)। अलग-अलग ऑब्जेक्ट, अलग-अलग RBAC। समन्वय की परेशानी नहीं [4]
- **Portable** — स्पेसिफिकेशन सभी implementations में एक समान है: Envoy Gateway, Istio, NGINX, Cilium, Kong, Traefik। vendor-specific annotations नहीं [4]

अगर आप आज नया क्लस्टर शुरू कर रहे हैं, तो Gateway API का उपयोग करें। प्रमुख क्लाउड प्रोवाइडर इसे सीधे सपोर्ट करते हैं। Ingress सालों तक काम करेगा लेकिन यह सिर्फ तकनीकी ऋण जमा कर रहा है [5]।

## बेयर मेटल के बारे में क्या?

क्लाउड प्रोवाइडर आपके लिए `LoadBalancer` Service की प्लंबिंग पारदर्शी रूप से जोड़ते हैं। बेयर मेटल पर — सेल्फ-मैनेज्ड VMs, ऑन-प्रेम रैक, k3s चलाने वाला होम लैब — कोई क्लाउड प्रोवाइडर नहीं होता। आपकी `type: LoadBalancer` Services अनिश्चित काल के लिए `<pending>` अवस्था में रहेंगी [6]।

**MetalLB** मानक समाधान है। यह आपके क्लस्टर को अपना IP पूल देता है और उन IPs को Layer 2 (ARP) या BGP के ज़रिए advertise करता है [7]। आप अपने लोकल नेटवर्क पर IPs की एक रेंज निर्धारित करते हैं, MetalLB को `IPAddressPool` के साथ कॉन्फ़िगर करते हैं, और यह LoadBalancer Services के लिए IP असाइनमेंट संभाल लेता है।

सामान्य बेयर-मेटल स्टैक:

1. MetalLB आपके पूल से Ingress Controller की Service को एक IP असाइन करता है
2. Ingress Controller (nginx-ingress, Traefik) HTTP रूटिंग और TLS संभालता है
3. आंतरिक सेवाएं ClusterIP पर रहती हैं

```yaml
# MetalLB के लिए IPs आरक्षित करें — नोड IPs या DHCP-प्रबंधित पते दोबारा उपयोग न करें
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

MetalLB फेलओवर भी संभालता है — अगर IP advertise करने वाला नोड डाउन हो जाता है, तो यह दूसरे नोड से re-advertise करता है। क्लाइंट के लिए IP स्थिर रहता है [7]।

## क्लाउड क्लस्टर: AWS EKS उदाहरण

EKS पर, आप **AWS Load Balancer Controller** इंस्टॉल करते हैं जो Kubernetes Service और Ingress ऑब्जेक्ट को असली AWS संसाधनों में बदलता है [8]। मैपिंग सीधी है:

| K8s ऑब्जेक्ट | AWS संसाधन | यह क्या करता है |
|---|---|---|
| `Service` (type LoadBalancer) | AWS Network Load Balancer (NLB) | L4, स्थिर IP, TCP/UDP |
| `Ingress` | AWS Application Load Balancer (ALB) | L7, WAF, Cognito, पाथ रूटिंग |
| `HTTPRoute` (Gateway API) | Gateway API controller के ज़रिए ALB | L7, आधुनिक declarative config |

एक बात जो मुझे परेशान कर चुकी है: **किसी मौजूदा Service पर `service.beta.kubernetes.io/aws-load-balancer-type` annotation कभी न बदलें।** अगर इसे बदलना ज़रूरी है, तो Service हटाएं और दोबारा बनाएं। इन-प्लेस बदलाव से AWS संसाधन लीक होते हैं जो साफ नहीं होते [8]।

EKS Auto Mode अब `LoadBalancer` Service बनाने पर NLB प्रोविज़निंग स्वचालित रूप से संभालता है — कोई अतिरिक्त controller इंस्टॉलेशन नहीं [8]। बुनियादी NLB ज़रूरतों से परे किसी भी चीज़ के लिए, Load Balancer Controller अभी भी सही टूल है।

## अंदर या बाहर? दोनों।

यह सवाल ही थोड़ा गलत है। **प्रोडक्शन Kubernetes लोड बैलेंसिंग हमेशा स्तरीय होती है**, एक चुनने का निर्णय नहीं:

- **क्लस्टर के बाहर** — एक क्लाउड LB या MetalLB स्थिर बाहरी endpoint प्रदान करता है और raw L4 ट्रैफ़िक संभालता है
- **क्लस्टर के किनारे पर (अंदर)** — एक Ingress Controller या Gateway API HTTP रूटिंग, TLS termination, रेट लिमिटिंग, और पाथ-आधारित नियम संभालता है
- **और अंदर** — ClusterIP Services पॉड्स के बीच सारा ईस्ट-वेस्ट ट्रैफ़िक संभालती हैं, बाहर से कुछ भी दिखाई नहीं देता

![k8s लोड बैलेंसर आर्किटेक्चर](/images/posts/kubernetes-load-balancer-options/k8s-load-balancer-architecture.svg)

इन सबको एक तंत्र में समेटने की कोशिश हमेशा परेशानी में डालती है। प्रति Service एक बाहरी LB महंगा है। क्लाउड NLB पर सीधे जटिल L7 रूटिंग करना अजीब है। Ingress Controller को L4 TCP राउटर की तरह इस्तेमाल करने के लिए हैक चाहिए। ये लेयर एक कारण से हैं।

NodePort वास्तव में केवल लोकल डेव या CI environments के लिए है। अगर कोई आपसे कहता है कि "इसे सरल रखने के लिए प्रोडक्शन में बस NodePort इस्तेमाल करो" — तो आपत्ति करें। आप इन्फ्रास्ट्रक्चर-स्तरीय लोड बैलेंसिंग को बायपास कर रहे हैं, नोड IPs पर निर्भर हो रहे हैं, और नॉन-स्टैंडर्ड फ़ायरवॉल पोर्ट खोल रहे हैं। पहले हफ्ते के बाद यह कुछ भी सरल नहीं करता।

> समाप्त

## स्रोत
1. [Services, Load Balancing, and Networking | Kubernetes](https://kubernetes.io/docs/concepts/services-networking/)
2. [Kubernetes Load Balancer: What Are the Options? | Komodor](https://komodor.com/learn/kubernetes-load-balancer-what-are-the-options/)
3. [The Ultimate Guide to Kubernetes Services, LoadBalancers, and Ingress | Robusta](https://home.robusta.dev/blog/kubernetes-service-vs-loadbalancer-vs-ingress)
4. [Understanding Kubernetes Gateway API: A Modern Approach to Traffic Management | CNCF](https://www.cncf.io/blog/2025/05/02/understanding-kubernetes-gateway-api-a-modern-approach-to-traffic-management/)
5. [Gateway API | Kubernetes](https://kubernetes.io/docs/concepts/services-networking/gateway/)
6. [Bare-metal considerations - Ingress-Nginx Controller](https://kubernetes.github.io/ingress-nginx/deploy/baremetal/)
7. [How to Deploy MetalLB with Nginx Ingress Controller | OneUptime](https://oneuptime.com/blog/post/2026-02-20-metallb-nginx-ingress/view)
8. [Load Balancing - Amazon EKS Best Practices](https://docs.aws.amazon.com/eks/latest/best-practices/load-balancing.html)