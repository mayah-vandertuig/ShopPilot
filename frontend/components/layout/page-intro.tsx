export function PageIntro({ title, description }: { title: string; description: string }) {
  return (
    <div>
      <h2 className="text-2xl font-bold text-foreground tracking-tight">{title}</h2>
      <p className="text-sm text-muted-foreground mt-1 max-w-2xl">{description}</p>
    </div>
  );
}
