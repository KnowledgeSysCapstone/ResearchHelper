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
import { queryAPI } from "@/api/queryAPI"

const formSchema = z.object({
    searchQuery: z.string().min(1, {
        message: "Search query cannot not be empty.",
    }),
})

export function SearchForm() {
    // 1. Define the form schema.
    const form = useForm<z.infer<typeof formSchema>>({
        resolver: zodResolver(formSchema),
        defaultValues: {
            searchQuery: "",
        },
    })
    
    // 2. Define a submit handler.
    // State for the result, loading.
    const [result, setResult] = useState<string | null>(null)
    const [loading, setLoading] = useState(false)

    async function onSubmit(values: z.infer<typeof formSchema>) {
      // Loading starts before api call. 
      setLoading(true) 

      try {
        // Making API call to the backend.
        //const response = await queryAPI(values.searchQuery)
        // The response contains the raw result.
        //setResult(response.data) // Set the result in state
      } catch (error) {
        //console.error("Error during API call: ", error)
        //setResult("An error occurred. Please try again.")
      } finally {
        setLoading(false)
      }
      alert("Claim entered.")
    }

  return (
    <Form {...form}>
      <form onSubmit={form.handleSubmit(onSubmit)} className="grid grid-cols-12 gap-4 items-center">
        {/* Input Field - spans majority of columns */}
        <div className="col-span-11">
          <FormField
            control={form.control}
            name="searchQuery"
            render={({ field }) => (
              <FormItem>
                <FormControl>
                  <Textarea className="w-full resize-none overflow-auto text-lg" placeholder="Enter your claim... " {...field} />
                </FormControl>
                <FormMessage className="text-destructive" />
              </FormItem>
            )}
          />
        </div>

        {/* Submit Button - spans 1 column */}
        <div className="col-span-1">
          <Button type="submit" variant="default" size="lg" className="rounded-full">Submit</Button>
        </div>
      </form>
    </Form>
  )
}
