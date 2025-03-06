export async function queryAPI(query: string) {
    const response = await fetch("REPLACEWITHENDPOINT", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ query }),
    })
  
    if (!response.ok) {
      throw new Error("Failed to fetch data.")
    }
  
    return response.json()
  }
  