import { Label } from "@/components/ui/label"

export function HomeLabel() {
  return (
    <div className="flex gap-4 justify-self-center">
      <img src="magnifying-glass.svg" alt="icon" width="56" height="56" />
      <Label className="text-6xl text-secondary-foreground">Claim Sourcer</Label>
    </div>
  )
}