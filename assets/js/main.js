(function () {
  "use strict";

  var root = document.documentElement;
  root.classList.remove("no-js");

  // Thai pages (th/) set <html lang="th">; pick the matching wording.
  var TH = root.lang === "th";
  function t(en, th) {
    return TH ? th : en;
  }

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
    toggle.setAttribute(
      "aria-label",
      open ? t("Close menu", "ปิดเมนู") : t("Open menu", "เปิดเมนู")
    );
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
      var TH_MONTHS = ["มกราคม", "กุมภาพันธ์", "มีนาคม", "เมษายน", "พฤษภาคม",
        "มิถุนายน", "กรกฎาคม", "สิงหาคม", "กันยายน", "ตุลาคม", "พฤศจิกายน", "ธันวาคม"];
      var thaiDate = function (iso) {
        var p = iso.split("-");
        // Thai Buddhist Era year: Gregorian + 543.
        return Number(p[2]) + " " + TH_MONTHS[Number(p[1]) - 1] + " " + (Number(p[0]) + 543);
      };
      // The calendar header's year box shows the Buddhist Era year (read-only,
      // since flatpickr parses whatever is typed there as a Gregorian year).
      var showThaiYear = function (a, b, inst) {
        var fp = inst || a;
        if (!fp || !fp.currentYearElement) return;
        fp.currentYearElement.readOnly = true;
        requestAnimationFrame(function () {
          fp.currentYearElement.value = fp.currentYear + 543;
        });
      };
      var checkStayLength = function () {
        var earliest = checkOut.min;
        var msg =
          checkOut.value && checkOut.value < earliest
            ? t(
                "Our minimum stay is " +
                  MIN_STAY_DAYS +
                  " days. Please choose a check-out date on or after " +
                  earliest +
                  ".",
                "เข้าพักขั้นต่ำ " +
                  MIN_STAY_DAYS +
                  " วัน กรุณาเลือกวันเช็คเอาท์ตั้งแต่ " +
                  thaiDate(earliest) +
                  " เป็นต้นไป"
              )
            : "";
        checkOut.setCustomValidity(msg);
        if (checkOut._flatpickr) checkOut._flatpickr.altInput.setCustomValidity(msg);
      };
      checkOut.min = addDays(today, MIN_STAY_DAYS);
      checkIn.addEventListener("change", function () {
        checkOut.min = addDays(checkIn.value || today, MIN_STAY_DAYS);
        if (checkOut.value && checkOut.value < checkOut.min) checkOut.value = "";
        if (checkOut._flatpickr) {
          checkOut._flatpickr.set("minDate", checkOut.min);
          if (!checkOut.value) checkOut._flatpickr.clear(false);
          showThaiYear(checkOut._flatpickr);
        }
        checkStayLength();
      });
      checkOut.addEventListener("input", checkStayLength);
      checkOut.addEventListener("change", checkStayLength);

      // Browsers draw native date pickers in the device's language, so the
      // Thai pages use flatpickr with its Thai locale for Thai months and days.
      if (TH) {
        var CDN = "https://cdnjs.cloudflare.com/ajax/libs/flatpickr/4.6.13/";
        var addCss = function (href) {
          var l = document.createElement("link");
          l.rel = "stylesheet";
          l.href = href;
          document.head.appendChild(l);
        };
        var addJs = function (src) {
          return new Promise(function (resolve, reject) {
            var sc = document.createElement("script");
            sc.src = src;
            sc.onload = resolve;
            sc.onerror = reject;
            document.head.appendChild(sc);
          });
        };
        addCss(CDN + "flatpickr.min.css");
        addCss(CDN + "themes/dark.min.css");
        addJs(CDN + "flatpickr.min.js")
          .then(function () {
            return addJs(CDN + "l10n/th.min.js");
          })
          .then(function () {
            var altFormat = "j F Y";
            var base = {
              locale: "th",
              dateFormat: "Y-m-d",
              altInput: true,
              altFormat: altFormat,
              // Show the Buddhist Era year in the field; keep Y-m-d for the email.
              formatDate: function (date, format) {
                if (format === altFormat) return thaiDate(window.flatpickr.formatDate(date, "Y-m-d"));
                return window.flatpickr.formatDate(date, format);
              },
              onReady: showThaiYear,
              onOpen: showThaiYear,
              onMonthChange: showThaiYear,
              onYearChange: showThaiYear,
              onChange: showThaiYear,
              altInputClass: "date-alt",
              disableMobile: true,
            };
            [checkIn, checkOut].forEach(function (input) {
              window.flatpickr(input, Object.assign({}, base, { minDate: input.min }));
              var alt = input._flatpickr.altInput;
              alt.required = input.required;
              alt.placeholder = "เลือกวันที่";
              var label = form.querySelector('label[for="' + input.id + '"]');
              if (label) {
                alt.id = input.id;
                input.removeAttribute("id");
              }
            });
          })
          .catch(function () {
            // If the CDN is unreachable the native date inputs still work.
          });
      }
    }

    var errorBox = form.querySelector("[data-form-error]");
    var successBox = form.querySelector("[data-form-success]");
    var submitBtn = form.querySelector('button[type="submit"]');

    // flatpickr's visible date fields are read-only, which browsers skip when
    // checking "required" - so ask for missing dates explicitly.
    var missingDate = function () {
      var empty = [checkIn, checkOut].filter(function (input) {
        return input && input._flatpickr && !input.value;
      })[0];
      if (!empty) return false;
      var alt = empty._flatpickr.altInput;
      alt.readOnly = false;
      alt.setCustomValidity(t("Please choose a date.", "กรุณาเลือกวันที่"));
      alt.reportValidity();
      var reset = function () {
        alt.readOnly = true;
        alt.setCustomValidity("");
      };
      alt.addEventListener("blur", reset, { once: true });
      empty.addEventListener("change", reset, { once: true });
      return true;
    };

    form.addEventListener("submit", function (e) {
      e.preventDefault();
      if (!form.reportValidity() || missingDate()) return;

      var el = form.elements;
      var to = form.getAttribute("data-to");
      var data = {
        _subject:
          "Booking enquiry — " +
          (el.bungalow.value || "Dalisay bungalow") +
          t("", " [TH]"),
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
      submitBtn.firstChild.textContent = t("Sending… ", "กำลังส่ง… ");

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
            t(
              "Sorry, your enquiry could not be sent. Please try again, or email us at ",
              "ขออภัย ไม่สามารถส่งคำถามได้ กรุณาลองอีกครั้ง หรือส่งอีเมลถึงเราที่ "
            ) +
            '<a href="mailto:' +
            to +
            '">' +
            to +
            "</a>" +
            t(".", "");
          errorBox.hidden = false;
        })
        .then(function () {
          submitBtn.disabled = false;
          submitBtn.firstChild.textContent = t("Send enquiry ", "ส่งคำถาม ");
        });
    });
  }

  /* ---------- Year ---------- */
  document.querySelectorAll("[data-year]").forEach(function (el) {
    el.textContent = new Date().getFullYear();
  });
})();
