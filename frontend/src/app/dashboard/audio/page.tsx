import AudioValidationForm from "@/components/modes/audio-form";

export default function DashboardAudioPage() {
  return (
    <section className="space-y-4">
      <div>
        <p className="text-xs uppercase tracking-[0.16em] text-white/60">Module</p>
        <h3 className="mt-1 text-2xl font-semibold">Audio Validation</h3>
        <p className="mt-1 text-sm text-white/75">
          Transcribe audio and classify dialect confidence for campaign quality.
        </p>
      </div>
      <AudioValidationForm />
    </section>
  );
}
