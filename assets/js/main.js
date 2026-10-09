/* GC Legal — comportamiento compartido: tema, navegación, menú móvil,
   filtro de servicios y formulario de contacto. Sin dependencias. */
(function () {
  "use strict";

  var root = document.documentElement;
  var body = document.body;

  function store(key, value) {
    try {
      if (value === undefined) return localStorage.getItem(key);
      localStorage.setItem(key, value);
    } catch (e) { return null; }
  }

  /* ---------- Tema claro / oscuro ---------- */
  function currentTheme() {
    var set = root.getAttribute("data-theme");
    if (set) return set;
    return window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
  }
  document.querySelectorAll("[data-theme-toggle]").forEach(function (btn) {
    btn.addEventListener("click", function () {
      var next = currentTheme() === "dark" ? "light" : "dark";
      root.setAttribute("data-theme", next);
      store("gc-theme", next);
      document.querySelectorAll("[data-theme-toggle]").forEach(function (b) {
        b.setAttribute("aria-label", next === "dark" ? "Cambiar a tema claro" : "Cambiar a tema oscuro");
      });
    });
    btn.setAttribute("aria-label", currentTheme() === "dark" ? "Cambiar a tema claro" : "Cambiar a tema oscuro");
  });

  /* ---------- Encabezado con sombra al hacer scroll ---------- */
  var header = document.querySelector(".site-header");
  if (header) {
    var onScroll = function () { header.classList.toggle("is-scrolled", window.scrollY > 8); };
    onScroll();
    window.addEventListener("scroll", onScroll, { passive: true });
  }

  /* ---------- Dropdown de servicios (escritorio) ---------- */
  document.querySelectorAll(".has-dropdown").forEach(function (item) {
    var trigger = item.querySelector(".nav-link");
    var closeTimer;
    function open() {
      clearTimeout(closeTimer);
      item.classList.add("is-open");
      trigger.setAttribute("aria-expanded", "true");
    }
    function close() {
      item.classList.remove("is-open");
      trigger.setAttribute("aria-expanded", "false");
    }
    trigger.addEventListener("click", function (e) {
      e.preventDefault();
      item.classList.contains("is-open") ? close() : open();
    });
    item.addEventListener("mouseenter", function () {
      if (window.matchMedia("(hover: hover)").matches) open();
    });
    item.addEventListener("mouseleave", function () {
      if (window.matchMedia("(hover: hover)").matches) closeTimer = setTimeout(close, 140);
    });
    item.addEventListener("focusout", function (e) {
      if (!item.contains(e.relatedTarget)) close();
    });
    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape" && item.classList.contains("is-open")) { close(); trigger.focus(); }
    });
    document.addEventListener("click", function (e) {
      if (!item.contains(e.target)) close();
    });
  });

  /* ---------- Menú lateral (móvil) ---------- */
  var drawer = document.getElementById("drawer");
  var menuBtn = document.querySelector(".menu-toggle");
  if (drawer && menuBtn) {
    var lastFocus = null;
    var focusables = function () {
      return drawer.querySelectorAll("a[href], button:not([disabled])");
    };
    var openDrawer = function () {
      lastFocus = document.activeElement;
      body.classList.add("drawer-open");
      drawer.removeAttribute("inert");
      drawer.setAttribute("aria-hidden", "false");
      menuBtn.setAttribute("aria-expanded", "true");
      var f = focusables();
      if (f.length) setTimeout(function () { f[0].focus(); }, 50);
    };
    var closeDrawer = function () {
      body.classList.remove("drawer-open");
      drawer.setAttribute("inert", "");
      drawer.setAttribute("aria-hidden", "true");
      menuBtn.setAttribute("aria-expanded", "false");
      if (lastFocus) lastFocus.focus();
    };
    menuBtn.addEventListener("click", openDrawer);
    document.querySelectorAll("[data-drawer-close]").forEach(function (el) {
      el.addEventListener("click", closeDrawer);
    });
    drawer.querySelectorAll("a[href^='#']").forEach(function (a) {
      a.addEventListener("click", closeDrawer);
    });
    document.addEventListener("keydown", function (e) {
      if (!body.classList.contains("drawer-open")) return;
      if (e.key === "Escape") { closeDrawer(); return; }
      if (e.key === "Tab") { // mantener el foco dentro del panel
        var f = focusables();
        var first = f[0], last = f[f.length - 1];
        if (e.shiftKey && document.activeElement === first) { e.preventDefault(); last.focus(); }
        else if (!e.shiftKey && document.activeElement === last) { e.preventDefault(); first.focus(); }
      }
    });
    window.matchMedia("(min-width: 1180px)").addEventListener("change", function (m) {
      if (m.matches && body.classList.contains("drawer-open")) closeDrawer();
    });
  }

  /* ---------- Filtro del directorio de servicios ---------- */
  var tablist = document.querySelector("[data-filter-tabs]");
  if (tablist) {
    var tabs = tablist.querySelectorAll("[role='tab']");
    var groups = document.querySelectorAll("[data-group]");
    var select = function (tab) {
      var value = tab.getAttribute("data-filter");
      tabs.forEach(function (t) {
        var on = t === tab;
        t.setAttribute("aria-selected", on ? "true" : "false");
        t.setAttribute("tabindex", on ? "0" : "-1");
      });
      groups.forEach(function (g) {
        g.hidden = !(value === "todos" || g.getAttribute("data-group") === value);
      });
    };
    tabs.forEach(function (tab, i) {
      tab.addEventListener("click", function () { select(tab); });
      tab.addEventListener("keydown", function (e) {
        var dir = e.key === "ArrowRight" ? 1 : e.key === "ArrowLeft" ? -1 : 0;
        if (!dir) return;
        e.preventDefault();
        var next = tabs[(i + dir + tabs.length) % tabs.length];
        next.focus();
        select(next);
      });
    });
    var hash = (location.hash || "").replace("#", "");
    tabs.forEach(function (t) { if (t.getAttribute("data-filter") === hash) select(t); });
  }

  /* ---------- Formulario de contacto ---------- */
  var form = document.getElementById("contact-form");
  if (form) {
    var wa = form.getAttribute("data-wa");
    var email = form.getAttribute("data-email");
    var status = document.getElementById("form-status");

    var preset = new URLSearchParams(location.search).get("servicio");
    if (preset && form.servicio) {
      Array.prototype.forEach.call(form.servicio.options, function (o) {
        if (o.value === preset) form.servicio.value = preset;
      });
    }

    var rules = {
      nombre: function (v) { return v.trim().length >= 2 || "Escribe tu nombre."; },
      email: function (v) { return /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(v.trim()) || "Escribe un correo válido."; },
      telefono: function (v) { return v.trim() === "" || /^[+\d\s()-]{7,}$/.test(v.trim()) || "Escribe un teléfono válido."; },
      servicio: function (v) { return v !== "" || "Selecciona el tipo de servicio."; },
      mensaje: function (v) { return v.trim().length >= 10 || "Cuéntanos un poco más sobre tu caso."; },
      consentimiento: function (_, el) { return el.checked || "Necesitamos tu autorización para responderte."; }
    };

    var validate = function () {
      var firstBad = null;
      Object.keys(rules).forEach(function (name) {
        var el = form.elements[name];
        if (!el) return;
        var res = rules[name](el.value, el);
        var field = el.closest(".field") || el.closest(".consent");
        var err = field && field.querySelector(".error");
        if (res === true) {
          el.removeAttribute("aria-invalid");
          if (field) field.classList.remove("has-error");
        } else {
          el.setAttribute("aria-invalid", "true");
          if (field) field.classList.add("has-error");
          if (err) err.textContent = res;
          if (!firstBad) firstBad = el;
        }
      });
      if (firstBad) firstBad.focus();
      return !firstBad;
    };

    var compose = function () {
      var f = form.elements;
      var lines = [
        "Hola, quiero consultar sobre los servicios de GC Legal.",
        "",
        "Nombre: " + f.nombre.value.trim(),
        "Correo: " + f.email.value.trim()
      ];
      if (f.telefono.value.trim()) lines.push("Teléfono: " + f.telefono.value.trim());
      lines.push("Servicio: " + f.servicio.options[f.servicio.selectedIndex].text);
      lines.push("", "Mensaje: " + f.mensaje.value.trim());
      return lines.join("\n");
    };

    var done = function (channel) {
      status.classList.add("is-visible", "is-success");
      status.querySelector("span").textContent = channel === "wa"
        ? "Abrimos WhatsApp con tu mensaje listo. Solo tienes que enviarlo y te respondemos en menos de 24 horas hábiles."
        : "Abrimos tu correo con el mensaje listo. Envíalo y te respondemos en menos de 24 horas hábiles.";
    };

    form.addEventListener("submit", function (e) {
      e.preventDefault();
      if (!validate()) return;
      window.open("https://wa.me/" + wa + "?text=" + encodeURIComponent(compose()), "_blank", "noopener");
      done("wa");
    });

    var mailBtn = document.getElementById("send-email");
    if (mailBtn) {
      mailBtn.addEventListener("click", function () {
        if (!validate()) return;
        var subject = "Consulta desde la web — " + form.servicio.options[form.servicio.selectedIndex].text;
        location.href = "mailto:" + email + "?subject=" + encodeURIComponent(subject) + "&body=" + encodeURIComponent(compose());
        done("mail");
      });
    }

    form.querySelectorAll("input, select, textarea").forEach(function (el) {
      el.addEventListener("input", function () {
        if (el.getAttribute("aria-invalid") !== "true") return;
        var rule = rules[el.name];
        if (rule && rule(el.value, el) === true) {
          el.removeAttribute("aria-invalid");
          var field = el.closest(".field") || el.closest(".consent");
          if (field) field.classList.remove("has-error");
        }
      });
    });
  }

  /* ---------- Año del pie de página ---------- */
  document.querySelectorAll("[data-year]").forEach(function (el) {
    el.textContent = new Date().getFullYear();
  });
})();
