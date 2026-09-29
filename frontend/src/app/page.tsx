import { redirect } from "next/navigation";

/** Public landing is off. Entry is the login screen. */
export default function Home() {
  redirect("/login");
}
