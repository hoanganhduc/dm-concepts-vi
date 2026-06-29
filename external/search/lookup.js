/* Quick-lookup instant filter for "Một số thuật ngữ trong Toán rời rạc".
 *
 * Pure client-side, no dependencies. Diacritics-insensitive matching so that
 * "so mau" finds "số màu", "do thi" finds "đồ thị", "cay khung" finds "cây
 * khung". Searches English headword, all Vietnamese variants, notation, and
 * definition, from a single entries.json (built from data/terms/*.yaml).
 */
(function () {
  "use strict";

  // Strip Vietnamese diacritics for accent-insensitive matching.
  function norm(s) {
    return (s || "")
      .normalize("NFD")
      .replace(/[̀-ͯ]/g, "") // strip combining diacritical marks
      .replace(/đ/g, "d").replace(/Đ/g, "D") // đ/Đ are NOT decomposed by NFD
      .toLowerCase()
      .trim();
  }

  function escapeHtml(s) {
    return (s || "").replace(/[&<>"]/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c];
    });
  }

  var ENTRIES = [];
  var activeLetter = "";
  var q = document.getElementById("q");
  var results = document.getElementById("results");
  var count = document.getElementById("count");
  var letterbar = document.getElementById("letters");

  function haystack(e) {
    return norm(
      [e.headword_en, e.notation, (e.vi_terms || []).join(" "), e.definition_vi].join("  ")
    );
  }

  function render(list) {
    results.innerHTML = "";
    count.textContent = list.length + " mục";
    var frag = document.createDocumentFragment();
    list.forEach(function (e) {
      var li = document.createElement("li");
      li.className = "entry";
      var vi = (e.vi_terms || []).join(", ");
      li.innerHTML =
        '<a class="hwline" href="' + e.url + '">' +
        '<span class="hw">' + escapeHtml(e.headword_en) + "</span>" +
        (e.notation ? ' <span class="nota">\\(' + escapeHtml(e.notation) + "\\)</span>" : "") +
        "</a>" +
        (vi ? ' <span class="vi">' + escapeHtml(vi) + "</span>" : "") +
        (e.definition_vi ? '<div class="defn">' + escapeHtml(e.definition_vi) + "</div>" : "");
      frag.appendChild(li);
    });
    results.appendChild(frag);
    if (window.MathJax && window.MathJax.typesetPromise) {
      window.MathJax.typesetPromise([results]);
    }
  }

  function apply() {
    var terms = norm(q.value).split(/\s+/).filter(Boolean);
    var list = ENTRIES;
    if (activeLetter) {
      list = list.filter(function (e) {
        return (e.letter || "").toUpperCase() === activeLetter;
      });
    }
    if (terms.length) {
      list = list.filter(function (e) {
        var h = haystack(e);
        return terms.every(function (t) { return h.indexOf(t) !== -1; });
      });
    }
    render(list);
  }

  function setActive(btn) {
    Array.prototype.forEach.call(letterbar.children, function (b) {
      b.classList.remove("active");
    });
    btn.classList.add("active");
  }

  function buildLetters() {
    var ls = Array.from(
      new Set(ENTRIES.map(function (e) { return (e.letter || "").toUpperCase(); }).filter(Boolean))
    ).sort();
    letterbar.innerHTML = "";
    var all = document.createElement("button");
    all.textContent = "Tất cả";
    all.onclick = function () { activeLetter = ""; setActive(all); apply(); };
    letterbar.appendChild(all);
    ls.forEach(function (L) {
      var b = document.createElement("button");
      b.textContent = L;
      b.onclick = function () { activeLetter = L; setActive(b); apply(); };
      letterbar.appendChild(b);
    });
    setActive(all);
  }

  q.addEventListener("input", apply);

  fetch("entries.json")
    .then(function (r) { return r.json(); })
    .then(function (data) {
      ENTRIES = data;
      buildLetters();
      apply();
      q.focus();
    })
    .catch(function () {
      results.innerHTML =
        "<li>Không tải được <code>entries.json</code>. " +
        "Hãy chạy <code>workflow/scripts/build-search-index.py</code> rồi mở lại trang.</li>";
    });
})();
