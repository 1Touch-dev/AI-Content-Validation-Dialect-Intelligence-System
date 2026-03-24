import ImageValidationForm from "@/components/modes/image-form";

export default function DashboardImagePage() {
  return (
    <section className="space-y-4">
      <div>
        <p className="text-xs uppercase tracking-[0.16em] text-white/60">Module</p>
        <h3 className="mt-1 text-2xl font-semibold">Image Validation</h3>
        <p className="mt-1 text-sm text-white/75">
          Run OCR safety checks and CLIP semantic scoring against expected context.
        </p>
      </div>
      <ImageValidationForm />
    </section>
  );
}
