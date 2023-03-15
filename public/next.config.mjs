// @ts-check
/**
 * Run `build` or `dev` with `SKIP_ENV_VALIDATION` to skip env validation.
 * This is especially useful for Docker builds.
 */
!process.env.SKIP_ENV_VALIDATION && (await import("./src/env/server.mjs"));

/** @type {import("next").NextConfig} */
const config = {
  reactStrictMode: true,
  output: 'standalone',
  swcMinify: true,
  i18n: {
    locales: ["en"],
    defaultLocale: "en",
  },
  // allow images from external domains
  images: {
    domains: ["user-images.githubusercontent.com"],
  },
  typescript: {
    ignoreBuildErrors: true,
  },
};
export default config;
