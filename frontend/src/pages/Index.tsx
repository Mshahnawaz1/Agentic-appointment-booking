import { Clock, Shield, MessageSquare, CalendarCheck, Stethoscope, Bell } from 'lucide-react';
import Header from '@/components/Header';
import ChatInterface from '@/components/ChatInterface';
import FeatureCard from '@/components/FeatureCard';

const features = [
  {
    icon: Clock,
    title: '24/7 Availability',
    description: 'Book appointments anytime, anywhere. Our AI assistant is always ready to help you.'
  },
  {
    icon: Shield,
    title: 'Secure & Private',
    description: 'Your health information is protected with enterprise-grade security and encryption.'
  },
  {
    icon: CalendarCheck,
    title: 'Instant Confirmation',
    description: 'Get immediate appointment confirmations and reminders sent to your phone.'
  },
  {
    icon: Stethoscope,
    title: 'Multiple Specialties',
    description: 'Access a wide range of medical specialties and healthcare providers.'
  },
  {
    icon: MessageSquare,
    title: 'Smart Assistance',
    description: 'Our AI understands your needs and suggests the best available appointment slots.'
  },
  {
    icon: Bell,
    title: 'Timely Reminders',
    description: 'Never miss an appointment with automated SMS and email reminders.'
  }
];

export default function Index() {
  return (
    <div className="min-h-screen bg-background">
      <Header />
      
      {/* Hero Section */}
      <section className="pt-32 md:pt-36 pb-20 px-6">
        <div className="container mx-auto">
          <div className="grid lg:grid-cols-2 gap-12 items-center">
            {/* Left Content */}
            <div className="animate-fade-in">
              <span className="inline-block px-4 py-1.5 bg-accent text-accent-foreground text-sm font-medium rounded-full mb-6">
                Healthcare Made Simple
              </span>
              <h1 className="text-4xl md:text-5xl lg:text-6xl font-bold text-foreground leading-tight mb-6">
                Book Your Hospital Appointment{' '}
                <span className="text-primary">Effortlessly</span>
              </h1>
              <p className="text-lg text-muted-foreground leading-relaxed mb-8 max-w-lg">
                Skip the phone calls and waiting times. Chat with our AI assistant to find and book the perfect appointment in seconds.
              </p>
              <div className="flex flex-wrap gap-4">
                <button className="px-8 py-4 bg-primary text-primary-foreground rounded-xl font-medium hover:bg-primary/90 transition-all hover:scale-105 active:scale-95 shadow-lg shadow-primary/25">
                  Start Booking Now
                </button>
                <button className="px-8 py-4 bg-secondary text-secondary-foreground rounded-xl font-medium hover:bg-secondary/80 transition-all">
                  Learn More
                </button>
              </div>
            </div>

            {/* Right Content - Chat Interface */}
            <div className="lg:pl-8">
              <ChatInterface />
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className="py-20 px-6 bg-muted/30">
        <div className="container mx-auto">
          <div className="text-center mb-16 animate-fade-in">
            <span className="inline-block px-4 py-1.5 bg-accent text-accent-foreground text-sm font-medium rounded-full mb-4">
              Features
            </span>
            <h2 className="text-3xl md:text-4xl font-bold text-foreground mb-4">
              Why Choose MediBook?
            </h2>
            <p className="text-muted-foreground max-w-2xl mx-auto">
              Experience the future of healthcare scheduling with our intelligent booking system.
            </p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {features.map((feature, index) => (
              <div key={feature.title} className="animate-slide-up" style={{ animationDelay: `${index * 0.1}s` }}>
                <FeatureCard {...feature} />
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 px-6">
        <div className="container mx-auto">
          <div className="bg-primary rounded-3xl p-12 md:p-16 text-center animate-fade-in">
            <h2 className="text-3xl md:text-4xl font-bold text-primary-foreground mb-4">
              Ready to Simplify Your Healthcare?
            </h2>
            <p className="text-primary-foreground/80 mb-8 max-w-xl mx-auto">
              Join thousands of patients who have already discovered the easier way to manage their healthcare appointments.
            </p>
            <button className="px-8 py-4 bg-background text-foreground rounded-xl font-medium hover:bg-background/90 transition-all hover:scale-105 active:scale-95">
              Get Started Today
            </button>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="py-12 px-6 border-t">
        <div className="container mx-auto">
          <div className="flex flex-col md:flex-row items-center justify-between gap-6">
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 bg-primary rounded-lg flex items-center justify-center">
                <CalendarCheck className="w-4 h-4 text-primary-foreground" />
              </div>
              <span className="font-semibold text-foreground">MediBook</span>
            </div>
            <p className="text-sm text-muted-foreground">
              © 2024 MediBook. All rights reserved.
            </p>
          </div>
        </div>
      </footer>
    </div>
  );
}
