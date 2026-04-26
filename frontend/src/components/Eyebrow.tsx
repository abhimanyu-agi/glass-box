interface Props { children: React.ReactNode; }

export default function Eyebrow({ children }: Props) {
  return (
    <p className="text-[11px] font-semibold uppercase tracking-[0.12em] text-muted-foreground">
      {children}
    </p>
  );
}