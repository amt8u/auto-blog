+++
title       = "Hugo Themes"
date        = 2024-11-01T18:00:00+05:30
draft       = false
toc         = true
description = "A curated look at Hugo themes — what makes a good theme, how to evaluate one, and the theme powering cloudmato.com."
+++

## Hugo Themes — What to Look For

Hugo has hundreds of themes. Most look fine in a screenshot and fall apart the moment you try to customise them. This page covers what actually matters when picking a theme, and highlights the one powering this site.

---

## What Makes a Good Hugo Theme

### Performance first

A theme that loads 400KB of JavaScript to render a blog is not a theme — it is a problem. Good Hugo themes ship minimal CSS, zero or near-zero JavaScript, and let Hugo's asset pipeline do the heavy lifting.

**Red flags:** bundled jQuery, icon fonts instead of SVG, unoptimised images baked into the theme, no asset fingerprinting.

### Multilingual support

If your audience spans more than one language, multilingual support is non-negotiable. This means i18n translation files per language, per-language menu configuration, and content that can be duplicated per language with separate slugs.

Hugo's built-in i18n system is excellent — but the theme has to be wired up for it. Many themes claim multilingual support and deliver only a language switcher.

### Clean markup

Themes that produce semantic HTML — proper heading hierarchy, `<article>`, `<nav>`, `<main>`, `<time>` — are far easier to style, index, and make accessible. Themes that use `<div>` for everything will fight you at every step.

### Active maintenance

Check the theme's GitHub repository. When was the last commit? Are issues being responded to? A theme that hasn't been touched in two years will start producing Hugo deprecation warnings the moment you upgrade.

### Override-friendly layout

Hugo's template lookup order means you can override any theme partial by creating the same file under your project's `layouts/` directory. Good themes are structured so that overrides are surgical — one partial for the header, one for the footer, one for each content type. Bad themes put everything in one file.

---

## The Theme Powering This Site

This site uses **[hugo-theme-monochrome](https://github.com/kaiiiz/hugo-theme-monochrome)** by kaiiiz.

### Why monochrome?

| Feature | Status |
|---|---|
| Multilingual / i18n | ✅ 56 languages including Hindi |
| Dark / light mode | ✅ Auto-detect + manual toggle |
| Table of contents | ✅ Right-side fixed panel |
| Site search | ✅ Built-in, no external service |
| Syntax highlighting | ✅ Prism.js with copy button |
| Math support | ✅ MathJax optional |
| Performance | ✅ Minimal JS, SCSS pipeline |
| Hugo version required | `>= 0.146.0` (extended) |

### Customisations on this site

- Feature images in post cards (image left, content right)
- Default fallback image for posts without a feature image
- Hindi i18n translation file added (`i18n/hi.toml`)
- Custom `user.css` injected via the theme's built-in hook

---

## Other Themes Worth Knowing

### [PaperMod](https://github.com/adityatelange/hugo-PaperMod)

The most popular Hugo theme on GitHub. Fast, clean, well-maintained, and genuinely multilingual. Good default choice for a blog or portfolio.

### [Blowfish](https://github.com/nunocoracao/blowfish)

Modern, feature-rich, built with Tailwind. Excellent documentation. Good fit for personal sites and developer portfolios.

### [Congo](https://github.com/jpanther/congo)

Hugo module-based, Tailwind-powered, strong i18n support. Very actively maintained.

### [Hextra](https://github.com/imfing/hextra)

Documentation-focused theme. Clean, fast, good search. Worth looking at if you need a docs site rather than a blog.

---

## Building Your Own Theme

Hugo themes are just Go templates, SCSS, and static assets. If none of the available themes fit exactly, it is entirely practical to:

1. Fork an existing theme and modify it
2. Start from a bare `baseof.html` and build up
3. Use a theme as a dependency via Hugo modules and override only the partials you need

The third approach is what this site does — monochrome is a git submodule, and only the partials that needed changes are overridden in the project's own `layouts/` directory.

---

*Have a theme to recommend? [Get in touch](mailto:cloudmato@gmail.com).*
