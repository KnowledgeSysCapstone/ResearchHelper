import { HomeLabel } from "@/components/home/homelabel";
import { SearchForm } from "@/components/home/searchform"

export default function Home() {
  return (
    <div className="flex flex-col items-center justify-center min-h-screen p-4 pb-20 gap-8 sm:p-8 md:p-12 font-[family-name:var(--font-geist-sans)]">
      <div className="w-full max-w-6xl">
        <HomeLabel />
        <h1 className="text-2xl font-bold text-center mb-8">Research Papers Vector Search</h1>
        <p className="text-gray-600 text-center mb-8">
          Enter your text, the system will use vector search to find the most similar sentences in research papers.
        </p>
      </div>
      <SearchForm />
    </div>
  );
}
