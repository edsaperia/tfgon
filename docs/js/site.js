// Tech for Good Organisers Network: the page's only script.
// Folding sections, the events list, the directory and its map, and the
// application form. The words of events and communities live in /docs/data.
(function () {
  'use strict';

  var config = window.TFGON_CONFIG || {};
  var PIN_COLOURS = ['var(--pink)', 'var(--yellow)', 'var(--green)', 'var(--blue)'];
  var OPEN_AT_START = ['intro-body'];

  // --- Small helpers -------------------------------------------------------

  function el(tag, attrs, children) {
    var node = document.createElement(tag);
    Object.keys(attrs || {}).forEach(function (key) {
      if (key === 'text') node.textContent = attrs[key];
      else if (key === 'className') node.className = attrs[key];
      else node.setAttribute(key, attrs[key]);
    });
    (children || []).forEach(function (child) {
      if (child == null) return;
      node.appendChild(typeof child === 'string' ? document.createTextNode(child) : child);
    });
    return node;
  }

  function link(href, text) {
    return el('a', { href: href, text: text || href.replace(/^https?:\/\//, '').replace(/\/$/, '') });
  }

  function tbc(text) {
    return el('span', { className: 'tbc', text: text || 'To be confirmed' });
  }

  // Words Ed still has to supply are written in [square brackets].
  function addressNode(address) {
    if (/^\[.*\]$/.test(address)) return el('span', { className: 'placeholder', text: address });
    return el('a', { href: 'mailto:' + address, text: address });
  }

  // --- Folding -------------------------------------------------------------

  function toggleFor(body) {
    return document.querySelector('.fold-toggle[aria-controls="' + body.id + '"]');
  }

  function setOpen(toggle, open) {
    var body = document.getElementById(toggle.getAttribute('aria-controls'));
    toggle.setAttribute('aria-expanded', String(open));
    if (open) body.removeAttribute('hidden');
    else body.setAttribute('hidden', 'until-found'); // find-in-page can still reach it
    var entry = toggle.closest('.community');
    if (entry) {
      entry.classList.toggle('is-open', open);
      var pin = document.querySelector('.pin[aria-controls="' + body.id + '"]');
      if (pin) pin.setAttribute('aria-expanded', String(open));
    }
  }

  function setUpFold(toggle) {
    var body = document.getElementById(toggle.getAttribute('aria-controls'));
    setOpen(toggle, OPEN_AT_START.indexOf(body.id) !== -1);
    toggle.addEventListener('click', function () {
      setOpen(toggle, toggle.getAttribute('aria-expanded') !== 'true');
    });
    body.addEventListener('beforematch', function () { setOpen(toggle, true); });
  }

  // Open every fold that contains the element with this id, then show it.
  function reveal(id, options) {
    var target = id && document.getElementById(id);
    if (!target) return false;
    var node = target;
    while (node) {
      if (node.classList && node.classList.contains('fold-body')) {
        var toggle = toggleFor(node);
        if (toggle) setOpen(toggle, true);
      }
      node = node.parentElement;
    }
    // A section's or entry's own body opens too.
    var ownToggle = target.querySelector('.fold-toggle');
    if (ownToggle && ownToggle.closest('.fold, .community, .past') === target) setOpen(ownToggle, true);
    if (!options || options.scroll !== false) target.scrollIntoView({ block: 'start' });
    return true;
  }

  function revealFromHash() {
    var id = decodeURIComponent(location.hash.slice(1));
    if (id) reveal(id);
  }

  // A link to the hash already in the address bar fires no hashchange, so
  // links inside the page reveal their target themselves.
  document.addEventListener('click', function (event) {
    var a = event.target.closest('a[href^="#"]');
    if (!a) return;
    var id = a.getAttribute('href').slice(1);
    if (id && id === decodeURIComponent(location.hash.slice(1))) reveal(id);
  });
  window.addEventListener('hashchange', revealFromHash);

  // --- Events --------------------------------------------------------------

  var dayFormat = new Intl.DateTimeFormat('en-GB', { weekday: 'long', day: 'numeric', month: 'long', year: 'numeric', timeZone: 'UTC' });
  var dayMonthFormat = new Intl.DateTimeFormat('en-GB', { day: 'numeric', month: 'long', timeZone: 'UTC' });

  function parseDay(iso) { return new Date(iso + 'T00:00:00Z'); }

  function todayIso() {
    var now = new Date();
    var pad = function (n) { return String(n).padStart(2, '0'); };
    return now.getFullYear() + '-' + pad(now.getMonth() + 1) + '-' + pad(now.getDate());
  }

  function eventDate(event) {
    if (!event.start) return event.year ? event.year + ', dates to be confirmed' : 'Dates to be confirmed';
    var start = parseDay(event.start);
    if (!event.end || event.end === event.start) return dayFormat.format(start);
    var end = parseDay(event.end);
    var sameMonth = start.getUTCMonth() === end.getUTCMonth() && start.getUTCFullYear() === end.getUTCFullYear();
    if (sameMonth) return start.getUTCDate() + '–' + dayMonthFormat.format(end) + ' ' + end.getUTCFullYear();
    return dayMonthFormat.format(start) + ' – ' + dayMonthFormat.format(end) + ' ' + end.getUTCFullYear();
  }

  function eventItem(event, upcoming) {
    var meta = [event.format, event.place, event.time].filter(Boolean).join(' · ');
    var date = event.start
      ? el('time', { className: 'event-date', datetime: event.start, text: eventDate(event) })
      : el('span', { className: 'event-date', text: eventDate(event) });
    return el('li', { className: 'event' + (upcoming ? ' event-upcoming' : '') }, [
      date,
      el('div', {}, [
        el('h4', { className: 'event-title', text: event.title }),
        meta ? el('p', { className: 'event-meta', text: meta }) : null,
        event.note ? el('p', { className: 'event-note', text: event.note }) : null
      ])
    ]);
  }

  function renderEvents(events) {
    var today = todayIso();
    var upcoming = events.filter(function (e) { return !e.start || (e.end || e.start) >= today; });
    var past = events.filter(function (e) { return upcoming.indexOf(e) === -1; });
    upcoming.sort(function (a, b) {
      if (!a.start || !b.start) return a.start ? -1 : b.start ? 1 : 0;
      return a.start < b.start ? -1 : 1;
    });
    past.sort(function (a, b) { return a.start < b.start ? 1 : -1; });

    var upcomingList = document.getElementById('events-upcoming');
    var pastList = document.getElementById('events-past');
    upcomingList.replaceChildren.apply(upcomingList, upcoming.length
      ? upcoming.map(function (e) { return eventItem(e, true); })
      : [el('li', { className: 'tbc', text: 'No meetings are planned yet.' })]);
    pastList.replaceChildren.apply(pastList, past.map(function (e) { return eventItem(e, false); }));
  }

  // --- Directory -----------------------------------------------------------

  function words(n) {
    return ['no', 'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'ten', 'eleven', 'twelve'][n] || String(n);
  }

  function listJoin(items) {
    if (items.length < 2) return items.join('');
    return items.slice(0, -1).join(', ') + ' and ' + items[items.length - 1];
  }

  function renderGlance(members, emerging) {
    var regions = [];
    members.forEach(function (c) { if (regions.indexOf(c.region) === -1) regions.push(c.region); });
    var text = words(members.length) + ' member communities, in ' + listJoin(regions) + '.';
    text = text.charAt(0).toUpperCase() + text.slice(1);
    if (emerging.length) {
      text += ' New groups are emerging in ' + listJoin(emerging.map(function (c) { return c.region; })) + '.';
    }
    var target = document.querySelector('#glance-communities .glance-text');
    target.replaceChildren(text + ' ', el('a', { href: '#directory', text: 'See the directory' }), '.');
  }

  function organiserNode(person) {
    var parts = [];
    if (person.photo) parts.push(el('img', { src: person.photo, alt: '', width: '40', height: '40', className: 'organiser-photo' }));
    parts.push(person.name);
    if (person.email) parts.push(' (', el('a', { href: 'mailto:' + person.email, text: person.email }), ')');
    return el('li', {}, parts);
  }

  function entryFor(community, colour) {
    var bodyId = 'community-' + community.id + '-body';
    var emerging = community.status === 'emerging';
    var toggle = el('button', { type: 'button', className: 'fold-toggle', 'aria-expanded': 'false', 'aria-controls': bodyId }, [
      el('span', { className: 'community-dot' + (emerging ? ' community-dot-emerging' : ''), 'aria-hidden': 'true' }),
      el('span', { className: 'community-name', text: community.name }),
      emerging ? el('span', { className: 'community-tag', text: 'Emerging' }) : null
    ]);
    var facts = [
      ['Region', document.createTextNode(community.region)],
      community.runBy ? ['Run by', document.createTextNode(community.runBy)] : null,
      ['Website', community.website ? link(community.website) : tbc()],
      ['Events', community.events ? link(community.events) : tbc()],
      ['Organisers', community.organisers.length
        ? el('ul', { className: 'organisers' }, community.organisers.map(organiserNode))
        : tbc('Not yet named')]
    ].filter(Boolean);
    var dl = el('dl', { className: 'entry-facts' });
    facts.forEach(function (fact) { dl.append(el('dt', { text: fact[0] }), el('dd', {}, [fact[1]])); });

    var item = el('li', { className: 'community', id: 'community-' + community.id }, [
      el('h3', { className: 'fold-heading' }, [toggle]),
      el('div', { className: 'fold-body', id: bodyId }, [
        community.about ? el('p', { className: 'entry-about', text: community.about }) : null,
        dl
      ])
    ]);
    item.style.setProperty('--pin', colour);
    return item;
  }

  function pinFor(community, colour, svg) {
    var emerging = community.status === 'emerging';
    var pin = el('button', {
      type: 'button',
      className: 'pin' + (emerging ? ' pin-emerging' : ''),
      'aria-controls': 'community-' + community.id + '-body',
      'aria-expanded': 'false',
      'data-community': community.id,
      'aria-label': community.name + (emerging ? ' (emerging)' : '') + ', ' + community.region,
      title: community.name
    });
    pin.style.setProperty('--pin', colour);
    if (!community.pin.online) {
      var box = svg.viewBox.baseVal;
      var west = Number(svg.dataset.west), north = Number(svg.dataset.north);
      var scale = Number(svg.dataset.scale), lat0 = Number(svg.dataset.lat0);
      var x = (community.pin.lon - west) * Math.cos(lat0 * Math.PI / 180) * scale;
      var y = (north - community.pin.lat) * scale;
      pin.style.left = (x / box.width * 100) + '%';
      pin.style.top = (y / box.height * 100) + '%';
    }
    pin.addEventListener('click', function () {
      var entry = document.getElementById('community-' + community.id);
      reveal(entry.id, { scroll: false });
      entry.scrollIntoView({ block: 'nearest' });
      entry.querySelector('.fold-toggle').focus({ preventScroll: true });
    });
    return pin;
  }

  function pastItem(community) {
    var meta = [community.region, community.years].filter(Boolean);
    var names = community.organisers.map(function (p) { return p.name; });
    if (names.length) meta.push((names.length > 1 ? 'Founding organisers: ' : 'Founding organiser: ') + listJoin(names));
    return el('li', { className: 'past-item', id: 'community-' + community.id }, [
      el('h4', { text: community.name }),
      el('p', { className: 'past-meta', text: meta.join(' · ') }),
      community.about ? el('p', { text: community.about }) : null,
      community.website ? el('p', {}, [link(community.website)]) : null
    ]);
  }

  function renderDirectory(communities) {
    var onMap = communities.filter(function (c) { return c.status === 'member' || c.status === 'emerging'; });
    var members = onMap.filter(function (c) { return c.status === 'member'; });
    var emerging = onMap.filter(function (c) { return c.status === 'emerging'; });
    var past = communities.filter(function (c) { return c.status === 'past'; });
    var ordered = members.concat(emerging);

    var svg = document.querySelector('#map .map-drawing');
    var list = document.getElementById('community-list');
    var pins = document.getElementById('map-pins');
    var onlinePins = document.getElementById('map-online-pins');

    var entries = [];
    ordered.forEach(function (community, i) {
      var colour = PIN_COLOURS[i % PIN_COLOURS.length];
      entries.push(entryFor(community, colour));
      (community.pin.online ? onlinePins : pins).appendChild(pinFor(community, colour, svg));
    });
    list.replaceChildren.apply(list, entries);
    document.getElementById('map-online').hidden = !onlinePins.children.length;
    list.querySelectorAll('.fold-toggle').forEach(setUpFold);

    var pastList = document.getElementById('past-list');
    pastList.replaceChildren.apply(pastList, past.map(pastItem));
    document.querySelector('.past').hidden = !past.length;

    renderGlance(members, emerging);
  }

  // --- Application form ----------------------------------------------------

  function setUpForm() {
    var form = document.getElementById('apply-form');
    var status = document.getElementById('apply-status');
    var linksList = document.getElementById('apply-links');
    var submit = form.querySelector('button[type="submit"]');
    var linkCount = 1;

    document.getElementById('apply-add-link').addEventListener('click', function () {
      linkCount += 1;
      var id = 'apply-link-' + linkCount;
      var input = el('input', { id: id, name: 'eventLinks', type: 'url', inputmode: 'url', placeholder: 'https://', 'aria-describedby': 'apply-links-hint' });
      linksList.appendChild(el('li', {}, [el('label', { className: 'visually-hidden', for: id, text: 'Event link ' + linkCount }), input]));
      input.focus();
    });

    function clearErrors() {
      form.querySelectorAll('.field-error').forEach(function (n) { n.remove(); });
      form.querySelectorAll('[aria-invalid]').forEach(function (n) {
        n.removeAttribute('aria-invalid');
        n.setAttribute('aria-describedby', (n.getAttribute('aria-describedby') || '').replace(/\s*\S+-error$/, ''));
      });
    }

    function markError(input, message) {
      var errorId = input.id + '-error';
      input.setAttribute('aria-invalid', 'true');
      input.setAttribute('aria-describedby', ((input.getAttribute('aria-describedby') || '') + ' ' + errorId).trim());
      input.insertAdjacentElement('afterend', el('span', { className: 'field-error', id: errorId, text: message }));
    }

    function validate() {
      clearErrors();
      var problems = [];
      var name = form.elements.name, email = form.elements.email;
      if (!name.value.trim()) problems.push([name, 'Enter your name.']);
      if (!email.value.trim()) problems.push([email, 'Enter an email address we can reply to.']);
      else if (!email.checkValidity()) problems.push([email, 'Enter an email address like name@example.org.']);
      var linkInputs = Array.prototype.slice.call(linksList.querySelectorAll('input'));
      var filled = linkInputs.filter(function (i) { return i.value.trim(); });
      if (!filled.length) problems.push([linkInputs[0], 'Add a link to at least one event you’ve organised.']);
      filled.forEach(function (i) {
        if (!/^https?:\/\/\S+\.\S+/.test(i.value.trim())) problems.push([i, 'Enter a full web address, starting with https://']);
      });
      problems.forEach(function (p) { markError(p[0], p[1]); });
      if (problems.length) problems[0][0].focus();
      return problems.length ? null : {
        name: name.value.trim(),
        email: email.value.trim(),
        eventLinks: filled.map(function (i) { return i.value.trim(); })
      };
    }

    function showFailure(reason) {
      status.className = 'form-status is-error';
      status.replaceChildren(
        el('p', {}, [el('strong', { text: 'Your application has not been sent.' }), ' ' + reason]),
        el('p', {}, ['Please email it to ', addressNode(config.fallbackEmail || ''), ' instead, with your name and links to the events you’ve organised.'])
      );
      status.focus();
    }

    function showSuccess() {
      status.className = 'form-status is-success';
      status.replaceChildren(
        el('p', {}, [el('strong', { text: 'Thank you. Your application has been sent.' })]),
        el('p', { text: 'We’ll reply to the email address you gave once we’ve looked at it.' })
      );
      status.focus();
    }

    form.addEventListener('submit', function (event) {
      event.preventDefault();
      status.className = 'form-status';
      status.replaceChildren();
      var application = validate();
      if (!application) return;

      // The trap field is hidden from people; only bots fill it in.
      if (form.elements.website.value) {
        showFailure('Something went wrong with the form.');
        return;
      }
      var endpoint = (config.applicationEndpoint || '').trim();
      if (!endpoint) {
        showFailure('Online applications are not switched on yet.');
        return;
      }

      submit.disabled = true;
      status.className = 'form-status';
      status.textContent = 'Sending…';
      var controller = new AbortController();
      var timer = setTimeout(function () { controller.abort(); }, 20000);
      fetch(endpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(application),
        signal: controller.signal
      }).then(function (response) {
        if (!response.ok) throw new Error('HTTP ' + response.status);
        form.reset();
        showSuccess();
      }).catch(function () {
        showFailure('Sending failed.');
      }).finally(function () {
        clearTimeout(timer);
        submit.disabled = false;
      });
    });
  }

  // --- Start ---------------------------------------------------------------

  document.querySelectorAll('.fold-toggle').forEach(setUpFold);
  setUpForm();

  function loadJson(path) {
    return fetch(path).then(function (r) {
      if (!r.ok) throw new Error(path + ': HTTP ' + r.status);
      return r.json();
    });
  }

  Promise.all([
    loadJson('data/events.json').then(function (d) { renderEvents(d.events); }, function () {
      document.getElementById('events-upcoming').replaceChildren(el('li', { className: 'tbc', text: 'The events list could not be loaded.' }));
    }),
    loadJson('data/communities.json').then(function (d) { renderDirectory(d.communities); }, function () {
      document.getElementById('community-list').replaceChildren(el('li', { className: 'tbc', text: 'The directory could not be loaded.' }));
    })
  ]).then(function () {
    document.documentElement.setAttribute('data-ready', '');
    revealFromHash();
  });
})();
