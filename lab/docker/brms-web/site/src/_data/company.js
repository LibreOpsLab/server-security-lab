// Company facts. The domain comes from the lab (LAB_DOMAIN, set in .env by Ansible and passed to the build),
// so the email addresses on the site match the lab's directory (lab/data/users.csv).
const domain = process.env.LAB_DOMAIN || "boab.lab";

export default {
  name: "Boab Ridge Mining Services",
  short: "Boab Ridge",
  motto: "Keep the site running",
  founded: "2011",
  phone: "(08) 5550 0142",
  address: ["1 Example Road", "Welshpool WA 6106"],
  hours: "Perth office: 7am to 5pm, Monday to Friday. Remote site office: 24 hours.",
  year: "2026",
  domain,
  // The shared mailboxes in lab/data/users.csv: who reads each one.
  mailboxes: [
    { name: "info", use: "General enquiries" },
    { name: "sales", use: "Quotes and new work" },
    { name: "service", use: "Jobs in progress and site visits" },
    { name: "accounts", use: "Invoices and payments" },
    { name: "hr", use: "Careers and employment" },
    { name: "security", use: "Report a security concern about our systems" },
  ],
};
