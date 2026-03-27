import ValidateForm from "@/components/validate-form";

export default function DashboardVideoPage() {
  return (
    <section className="space-y-4">
      <div>
        <p className="text-xs uppercase tracking-[0.16em] text-white/60">Module</p>
        <h3 className="mt-1 text-2xl font-semibold">Video Validation</h3>
        <p className="mt-1 text-sm text-white/75">
          Full end-to-end pipeline combining speech, dialect, OCR, and vision checks.
        </p>
      </div>
      <ValidateForm />
    </section>
  );
}
