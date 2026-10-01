(function () {
  "use strict";

  var root = document.documentElement;
  root.classList.remove("no-js");

  /* ---------- Header: solid on scroll ---------- */
  var header = document.querySelector(".site-header");
  var hasHero = document.querySelector("[data-hero]");

  function onScroll() {
    if (!header) return;
    var solid = !hasHero || window.scrollY > 40;
    header.classList.toggle("is-solid", solid);
  }

  onScroll();
  window.addEventListener("scroll", onScroll, { passive: true });

  /* ---------- Mobile menu ---------- */
  var toggle = document.querySelector(".menu-toggle");
  var menu = document.getElementById("mobile-menu");

  function setMenu(open) {
    document.body.classList.toggle("menu-open", open);
    toggle.setAttribute("aria-expanded", String(open));
    toggle.setAttribute("aria-label", open ? "Close menu" : "Open menu");
    menu.setAttribute("aria-hidden", String(!open));
    document.body.style.overflow = open ? "hidden" : "";
  }

  if (toggle && menu) {
    toggle.addEventListener("click", function () {
      setMenu(!document.body.classList.contains("menu-open"));
    });

    menu.addEventListener("click", function (e) {
      if (e.target.closest("a")) setMenu(false);
    });

    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape" && document.body.classList.contains("menu-open")) {
        setMenu(false);
        toggle.focus();
      }
    });
  }

  /* ---------- Reveal on scroll ---------- */
  var revealables = document.querySelectorAll(".reveal, .line-drawing.draw");

  if ("IntersectionObserver" in window) {
    var io = new IntersectionObserver(
      function (entries) {
        entries.forEach(function (entry) {
          if (entry.isIntersecting) {
            entry.target.classList.add("is-visible");
            io.unobserve(entry.target);
          }
        });
      },
      { rootMargin: "0px 0px -8% 0px", threshold: 0.08 }
    );
    revealables.forEach(function (el) {
      io.observe(el);
    });
  } else {
    revealables.forEach(function (el) {
      el.classList.add("is-visible");
    });
  }

  /* ---------- Bungalow sub-nav active state ---------- */
  var subLinks = document.querySelectorAll(".bungalow-nav a[href^='#']");

  if (subLinks.length && "IntersectionObserver" in window) {
    var sections = Array.prototype.map.call(subLinks, function (a) {
      return document.querySelector(a.getAttribute("href"));
    });

    var subIo = new IntersectionObserver(
      function (entries) {
        entries.forEach(function (entry) {
          if (!entry.isIntersecting) return;
          subLinks.forEach(function (a) {
            a.classList.toggle(
              "is-active",
              a.getAttribute("href") === "#" + entry.target.id
            );
          });
        });
      },
      { rootMargin: "-40% 0px -55% 0px" }
    );

    sections.forEach(function (s) {
      if (s) subIo.observe(s);
    });
  }

  /* ---------- Gallery filters ---------- */
  var filterBar = document.querySelector("[data-filters]");

  if (filterBar) {
    var items = document.querySelectorAll("[data-gallery] [data-cat]");

    filterBar.addEventListener("click", function (e) {
      var btn = e.target.closest("button[data-filter]");
      if (!btn) return;
      var f = btn.getAttribute("data-filter");

      filterBar.querySelectorAll("button").forEach(function (b) {
        b.setAttribute("aria-pressed", String(b === btn));
      });

      items.forEach(function (item) {
        var cats = item.getAttribute("data-cat").split(" ");
        item.hidden = !(f === "all" || cats.indexOf(f) !== -1);
      });
    });
  }

  /* ---------- Lightbox ---------- */
  var lightbox = document.getElementById("lightbox");

  if (lightbox) {
    var lbImg = lightbox.querySelector("img");
    var lbCount = lightbox.querySelector("[data-count]");
    var lbCaption = lightbox.querySelector("[data-caption]");
    var group = [];
    var index = 0;
    var lastFocus = null;

    function visibleIn(container) {
      return Array.prototype.filter.call(
        container.querySelectorAll("button[data-full]"),
        function (b) {
          return !b.hidden;
        }
      );
    }

    function show(i) {
      index = (i + group.length) % group.length;
      var btn = group[index];
      var img = btn.querySelector("img");
      lbImg.src = btn.getAttribute("data-full");
      lbImg.alt = img ? img.alt : "";
      lbCaption.textContent = btn.getAttribute("data-caption") || "";
      lbCount.textContent =
        String(index + 1).padStart(2, "0") +
        " / " +
        String(group.length).padStart(2, "0");
    }

    function open(container, btn) {
      group = visibleIn(container);
      lastFocus = btn;
      show(group.indexOf(btn));
      lightbox.classList.add("is-open");
      lightbox.setAttribute("aria-hidden", "false");
      document.body.style.overflow = "hidden";
      lightbox.querySelector("[data-close]").focus();
    }

    function close() {
      lightbox.classList.remove("is-open");
      lightbox.setAttribute("aria-hidden", "true");
      document.body.style.overflow = "";
      if (lastFocus) lastFocus.focus();
    }

    document.addEventListener("click", function (e) {
      var btn = e.target.closest("button[data-full]");
      if (!btn) return;
      var container = btn.closest("[data-lightbox-group]");
      if (container) open(container, btn);
    });

    lightbox.querySelector("[data-close]").addEventListener("click", close);
    lightbox.querySelector("[data-prev]").addEventListener("click", function () {
      show(index - 1);
    });
    lightbox.querySelector("[data-next]").addEventListener("click", function () {
      show(index + 1);
    });

    lightbox.addEventListener("click", function (e) {
      if (e.target.classList.contains("lightbox__stage")) close();
    });

    document.addEventListener("keydown", function (e) {
      if (!lightbox.classList.contains("is-open")) return;
      if (e.key === "Escape") close();
      if (e.key === "ArrowLeft") show(index - 1);
      if (e.key === "ArrowRight") show(index + 1);
    });

    var touchX = null;
    lightbox.addEventListener(
      "touchstart",
      function (e) {
        touchX = e.touches[0].clientX;
      },
      { passive: true }
    );
    lightbox.addEventListener("touchend", function (e) {
      if (touchX === null) return;
      var dx = e.changedTouches[0].clientX - touchX;
      if (Math.abs(dx) > 50) show(index + (dx < 0 ? 1 : -1));
      touchX = null;
    });
  }

  /* ---------- Enquiry form -> email (via FormSubmit) ---------- */
  var form = document.querySelector("[data-enquiry]");

  if (form) {
    var params = new URLSearchParams(window.location.search);
    var preset = params.get("bungalow");
    if (preset && form.elements.bungalow) {
      form.elements.bungalow.value = preset;
    }

    var checkIn = form.elements.checkin;
    var checkOut = form.elements.checkout;
    var today = new Date().toISOString().slice(0, 10);
    var MIN_STAY_DAYS = 30;
    var addDays = function (isoDate, days) {
      var d = new Date(isoDate + "T00:00:00Z");
      d.setUTCDate(d.getUTCDate() + days);
      return d.toISOString().slice(0, 10);
    };
    if (checkIn) checkIn.min = today;
    if (checkIn && checkOut) {
      var checkStayLength = function () {
        var earliest = checkOut.min;
        checkOut.setCustomValidity(
          checkOut.value && checkOut.value < earliest
            ? "Our minimum stay is " +
                MIN_STAY_DAYS +
                " days. Please choose a check-out date on or after " +
                earliest +
                "."
            : ""
        );
      };
      checkOut.min = addDays(today, MIN_STAY_DAYS);
      checkIn.addEventListener("change", function () {
        checkOut.min = addDays(checkIn.value || today, MIN_STAY_DAYS);
        if (checkOut.value && checkOut.value < checkOut.min) checkOut.value = "";
        checkStayLength();
      });
      checkOut.addEventListener("input", checkStayLength);
      checkOut.addEventListener("change", checkStayLength);
    }

    var errorBox = form.querySelector("[data-form-error]");
    var successBox = form.querySelector("[data-form-success]");
    var submitBtn = form.querySelector('button[type="submit"]');

    form.addEventListener("submit", function (e) {
      e.preventDefault();
      if (!form.reportValidity()) return;

      var el = form.elements;
      var to = form.getAttribute("data-to");
      var data = {
        _subject:
          "Booking enquiry — " + (el.bungalow.value || "Dalisay bungalow"),
        _template: "table",
        _captcha: "false",
        _honey: el._honey.value,
        name: el.name.value,
        email: el.email.value,
        bungalow: el.bungalow.value || "No preference",
        checkin: el.checkin.value || "-",
        checkout: el.checkout.value || "-",
        guests: el.guests.value,
        message: el.message.value || "-",
      };

      errorBox.hidden = true;
      submitBtn.disabled = true;
      submitBtn.firstChild.textContent = "Sending… ";

      fetch("https://formsubmit.co/ajax/" + to, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Accept: "application/json",
        },
        body: JSON.stringify(data),
      })
        .then(function (res) {
          return res.json().then(function (json) {
            if (!res.ok || String(json.success) !== "true") {
              throw new Error(json.message || "Send failed");
            }
          });
        })
        .then(function () {
          Array.prototype.forEach.call(form.children, function (child) {
            if (child !== successBox) child.hidden = true;
          });
          successBox.hidden = false;
          successBox.focus();
        })
        .catch(function () {
          errorBox.innerHTML =
            'Sorry, your enquiry could not be sent. Please try again, or email us at <a href="mailto:' +
            to +
            '">' +
            to +
            "</a>.";
          errorBox.hidden = false;
        })
        .then(function () {
          submitBtn.disabled = false;
          submitBtn.firstChild.textContent = "Send enquiry ";
        });
    });
  }

  /* ---------- Year ---------- */
  document.querySelectorAll("[data-year]").forEach(function (el) {
    el.textContent = new Date().getFullYear();
  });
})();
