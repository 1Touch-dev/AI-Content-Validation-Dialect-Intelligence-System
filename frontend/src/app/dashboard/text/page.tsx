import TextValidationForm from "@/components/modes/text-form";

export default function DashboardTextPage() {
  return (
    <section className="space-y-4">
      <div>
        <p className="text-xs uppercase tracking-[0.16em] text-white/60">Module</p>
        <h3 className="mt-1 text-2xl font-semibold">Text Validation</h3>
        <p className="mt-1 text-sm text-white/75">
          Submit Spanish text and detect Honduras dialect alignment confidence.
        </p>
      </div>
      <TextValidationForm />
    </section>
  );
}
