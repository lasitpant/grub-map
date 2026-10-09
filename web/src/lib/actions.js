import { computed, ref } from "vue";
import { euro } from "./store";
import { track } from "./analytics";

export const host = (url) => { try { return new URL(url).hostname.replace(/^www\./, ""); } catch { return url; } };

// Directions, share and click tracking for one venue (a computed ref), used by the pin popup and the full menu panel.
export function useVenueActions(venue) {
  // Walking directions in Google Maps (opens the app on phones if installed).
  // Hand-placed venues use a name search instead, since their pin is only approximate.
  const directionsUrl = computed(() => {
    const v = venue.value;
    if (!v) return "";
    const base = "https://www.google.com/maps/dir/?api=1&travelmode=walking&destination=";
    return base + encodeURIComponent(v.approx ? `${v.name}, Dublin` : `${v.lat},${v.lon}`);
  });
  const clicked = (kind) => track(`${kind}/${venue.value.brand}`, `${venue.value.name} · ${kind}`);

  // Share this venue: the phone's share sheet where available, otherwise copy the link.
  const shareNote = ref("");
  async function share() {
    const v = venue.value;
    const url = `${location.origin}${location.pathname}#${v.id}`;
    const text = `${v.name}: lunch from ${euro(v.price)} on Grub Map`;
    clicked("share");
    try {
      if (navigator.share) return await navigator.share({ title: v.name, text, url });
      await navigator.clipboard.writeText(url);
      shareNote.value = "Link copied";
    } catch (e) {
      if (e?.name !== "AbortError") shareNote.value = url; // clipboard blocked: show the link to copy by hand
    }
    setTimeout(() => (shareNote.value = ""), 4000);
  }

  return { directionsUrl, clicked, share, shareNote };
}
