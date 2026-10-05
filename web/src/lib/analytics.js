// Privacy-friendly analytics via GoatCounter (https://www.goatcounter.com).
// No cookies, no IP addresses stored, nothing that identifies a person.
// Disabled unless VITE_GOATCOUNTER_CODE is set; GoatCounter also ignores localhost by default.
const CODE = import.meta.env.VITE_GOATCOUNTER_CODE;
const queue = [];

export function initAnalytics() {
  if (!CODE) return;
  const s = document.createElement("script");
  s.async = true;
  s.src = "https://gc.zgo.at/count.js";
  s.dataset.goatcounter = `https://${CODE}.goatcounter.com/count`;
  s.onload = () => queue.splice(0).forEach((e) => window.goatcounter?.count(e));
  document.head.appendChild(s);
}

// Count an anonymous event, e.g. track("venue/aobaba", "Aobaba · list").
// Events show in the GoatCounter dashboard as their own "paths".
export function track(path, title = path) {
  if (!CODE) return;
  const e = { path, title, event: true };
  window.goatcounter?.count ? window.goatcounter.count(e) : queue.push(e);
}
