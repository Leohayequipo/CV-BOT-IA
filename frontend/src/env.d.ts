// Settings the build reads from the environment. Deployments set them; locally, copy
// .env.example to .env.
interface ImportMetaEnv {
  // The API's address, such as https://api.<domain>; locally, http://localhost:8001
  readonly VITE_API_URL?: string;
  // Leonardo's phone number, for the WhatsApp link. Never committed (ADR-016)
  readonly VITE_CONTACT_PHONE?: string;
  // Where the CV PDF is published (step 1.7); without it, the download button is hidden
  readonly VITE_CV_URL?: string;
}
