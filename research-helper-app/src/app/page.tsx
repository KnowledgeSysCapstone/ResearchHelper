import { SearchForm } from "@/components/home/searchform"

export default function Home() {
  return (
    <div className="grid grid-rows-[40px_1fr_40px] items-center justify-items-center min-h-screen p-8 pb-20 gap-16 sm:p-20 font-[family-name:var(--font-geist-sans)]">
      <SearchForm />
    </div>
  );
}
