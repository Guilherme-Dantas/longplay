export const colors = {
  bg: "#000000",
  text: "#ededed",
  mute: "#888888",
  line: "rgba(255, 255, 255, 0.14)",
  glass: "rgba(255, 255, 255, 0.06)",
  glassRaised: "rgba(255, 255, 255, 0.08)",
  field: "rgba(255, 255, 255, 0.04)",
  solid: "#141416",
  cardShadow: "0 24px 80px rgba(0, 0, 0, 0.45)",
  washBlue: "rgba(150, 180, 255, 0.22)",
  washWhite: "rgba(255, 255, 255, 0.1)",
};

export const coverTones = ["#2c4f8a", "#4a3058", "#1d4038", "#5a3a2c", "#2e3848"] as const;

export function toneFor(albumId: string): string {
  let index = 0;
  for (let i = 0; i < albumId.length; i += 1) {
    index = (index + albumId.charCodeAt(i)) % coverTones.length;
  }
  return coverTones[index] ?? coverTones[0];
}
