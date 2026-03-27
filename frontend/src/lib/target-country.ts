export const TARGET_COUNTRIES = [
  { value: "honduras", label: "Honduras 🇭🇳" },
  { value: "ecuador", label: "Ecuador 🇪🇨" },
] as const;

export type TargetCountry = (typeof TARGET_COUNTRIES)[number]["value"];

export function getDefaultText(country: TargetCountry): string {
  return country === "ecuador"
    ? "Habla nanyo, que tal todo por Guayaquil?"
    : "Vos sos maje si pensas que salir temprano es facil.";
}

export function getDefaultTopic(country: TargetCountry): string {
  return country === "ecuador"
    ? "Ecuador scenery, beautiful people"
    : "Honduras scenery, beautiful people";
}
