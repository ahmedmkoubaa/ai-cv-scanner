import "@testing-library/jest-dom";

if (!globalThis.crypto) {
  // @ts-expect-error mock crypto in test environment
  globalThis.crypto = {};
}

if (!globalThis.crypto.randomUUID) {
  globalThis.crypto.randomUUID = () =>
    "12345678-1234-4234-8234-123456789abc";
}
