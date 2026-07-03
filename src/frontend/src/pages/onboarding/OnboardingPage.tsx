import { useState } from 'react'
import { useNavigate } from 'react-router-dom'

const slides = [
  {
    headline: 'Save together, win together',
    sub: 'Join trusted ajo circles with people you know.',
  },
  {
    headline: 'Your turn always comes',
    sub: 'Transparent rotation so everyone knows when they receive.',
  },
  {
    headline: 'Secured by Nomba',
    sub: 'Every contribution hits a dedicated virtual account — no middleman.',
  },
]

export default function OnboardingPage() {
  const [step, setStep] = useState(0)
  const navigate = useNavigate()

  const isLast = step === slides.length - 1
  const { headline, sub } = slides[step]

  function finish() {
    navigate('/login', { replace: true })
  }

  return (
    <main className="w-full max-w-[480px] bg-[#F8F5F0] min-h-svh shadow-[0_0_48px_rgba(27,67,50,0.10)] flex flex-col px-7 pb-9 pt-5">
      {/* Skip */}
      <div className="flex justify-end">
        <button
          onClick={finish}
          className="text-sm font-semibold text-[#6B7268] bg-transparent border-none cursor-pointer"
        >
          Skip
        </button>
      </div>

      {/* Illustration + text */}
      <div className="flex-1 flex flex-col items-center justify-center gap-9">
        <div
          className="w-full max-w-[280px] aspect-square rounded-3xl border border-[#E1DACB] flex items-center justify-center"
          style={{
            background:
              'repeating-linear-gradient(135deg, #EDE7DA, #EDE7DA 12px, #F3EEE3 12px, #F3EEE3 24px)',
          }}
          aria-hidden="true"
        >
          <span className="font-mono text-xs text-[#9A9384]">
            illustration {step + 1}/3
          </span>
        </div>

        <div className="flex flex-col items-center gap-3 text-center">
          <h1 className="text-[26px] font-extrabold text-[#1B4332] leading-snug tracking-[-0.5px] m-0 max-w-[300px]">
            {headline}
          </h1>
          <p className="text-[15px] text-[#6B7268] leading-relaxed max-w-[300px] m-0">
            {sub}
          </p>
        </div>
      </div>

      {/* Dots + button */}
      <div className="flex flex-col items-center gap-[22px]">
        <div className="flex gap-2" role="tablist" aria-label="Onboarding progress">
          {slides.map((_, i) => (
            <span
              key={i}
              role="tab"
              aria-selected={i === step}
              aria-label={`Slide ${i + 1} of ${slides.length}`}
              className="h-2 rounded-full transition-all duration-300"
              style={{
                width: i === step ? '24px' : '8px',
                background: i === step ? '#1B4332' : '#DDD6C8',
              }}
            />
          ))}
        </div>

        <button
          onClick={() => (isLast ? finish() : setStep(step + 1))}
          className="w-full py-4 bg-[#1B4332] text-[#F8F5F0] rounded-xl text-base font-bold border-none cursor-pointer hover:bg-[#173A2B] transition-colors"
        >
          {isLast ? 'Get started' : 'Next'}
        </button>
      </div>
    </main>
  )
}
