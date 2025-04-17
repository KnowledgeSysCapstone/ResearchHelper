"use client"

import { zodResolver } from "@hookform/resolvers/zod"
import { useForm } from "react-hook-form"
import { z } from "zod"
import { useState } from "react"

import { Button } from "@/components/ui/button"
import {
  Form,
  FormControl,
  FormDescription,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form"
import { Textarea } from "@/components/ui/textarea"
import { vectorSearchAPI } from "@/api/queryAPI"
import { SearchResults } from "./SearchResults"

const formSchema = z.object({
    searchQuery: z.string().min(1, {
        message: "Search content cannot be empty.",
    }),
})

export function SearchForm() {
    // 1. Define form
    const form = useForm<z.infer<typeof formSchema>>({
        resolver: zodResolver(formSchema),
        defaultValues: {
            searchQuery: "",
        },
    })
    
    // 2. Define state
    const [results, setResults] = useState<any[]>([])
    const [loading, setLoading] = useState(false)
    const [error, setError] = useState<string | null>(null)

    // 3. Submit handler
    async function onSubmit(values: z.infer<typeof formSchema>) {
      // Reset state
      setError(null)
      setLoading(true)

      try {
        // Call vector search API
        const response = await vectorSearchAPI(values.searchQuery);
        setResults(response)
      } catch (error) {
        console.error("Error during API call: ", error)
        setError("An error occurred during search. Please try again later.")
      } finally {
        setLoading(false)
      }
    }

  return (
    <div className="w-full max-w-6xl">
      <Form {...form}>
        <form onSubmit={form.handleSubmit(onSubmit)}>
          {/* Input field - occupies most columns */}
          <div className="grid grid-cols-1 gap-5 justify-items-center">
          <div>
            <FormField
              control={form.control}
              name="searchQuery"
              render={({ field }) => (
                <FormItem>
                  <FormControl>
                    <Textarea 
                      className="w-2xl resize-none overflow-auto text-lg" 
                      placeholder="Enter your search text..." 
                      {...field} 
                    />
                  </FormControl>
                  <FormMessage className="text-destructive" />
                </FormItem>
              )}
            />
          </div>

          {/* Submit button - occupies 1 column */}
          <div>
            <Button 
              type="submit" 
              variant="default" 
              size="lg" 
              className="rounded-full"
              disabled={loading}
            >
              {loading ? 'Searching...' : 'Search'}
            </Button>
          </div>
          </div>
        </form>
      </Form>

      {/* Search results display */}
      <SearchResults 
        results={results} 
        isLoading={loading} 
        error={error}
      />
    </div>
  )
}
