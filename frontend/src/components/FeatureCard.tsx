import { LucideIcon } from 'lucide-react';

interface FeatureCardProps {
  icon: LucideIcon;
  title: string;
  description: string;
}

export default function FeatureCard({ icon: Icon, title, description }: FeatureCardProps) {
  return (
    <div className="group p-6 bg-card rounded-2xl border hover:border-primary/30 transition-all duration-300 hover:shadow-lg hover:-translate-y-1">
      <div className="w-12 h-12 bg-accent rounded-xl flex items-center justify-center mb-4 group-hover:bg-primary/10 transition-colors">
        <Icon className="w-6 h-6 text-accent-foreground group-hover:text-primary transition-colors" />
      </div>
      <h3 className="text-lg font-semibold text-foreground mb-2">{title}</h3>
      <p className="text-sm text-muted-foreground leading-relaxed">{description}</p>
    </div>
  );
}
