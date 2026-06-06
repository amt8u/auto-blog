// Highlight only the topmost section currently visible in the viewport,
// not every section that happens to intersect (the theme default). Project
// override of themes/hugo-theme-monochrome/assets/js/toc-tracker.js.

window.addEventListener('DOMContentLoaded', () => {
    const sections = Array.from(document.querySelectorAll('section[id]'));
    if (sections.length === 0) return;

    const visible = new Set();

    const setActive = () => {
        // Document-order traversal: the first section in `sections` that is in
        // `visible` is the topmost one currently on screen.
        const topmost = sections.find((s) => visible.has(s));

        // Clear any prior active state, then mark the topmost.
        document
            .querySelectorAll('#TableOfContents li.active')
            .forEach((li) => li.classList.remove('active'));

        if (!topmost) return;
        const link = document.querySelector(
            `#TableOfContents li a[href="#${topmost.getAttribute('id')}"]`,
        );
        if (link) link.parentElement.classList.add('active');
    };

    const observer = new IntersectionObserver((entries) => {
        for (const entry of entries) {
            if (entry.isIntersecting) {
                visible.add(entry.target);
            } else {
                visible.delete(entry.target);
            }
        }
        setActive();
    });

    sections.forEach((section) => observer.observe(section));
});
