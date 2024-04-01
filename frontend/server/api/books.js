export default defineEventHandler(async (event) => {
  const query = getQuery(event);

  // Ensure you properly encode the query parameter to be used in the URL
  const response = await fetch(
    `${process.env.BE_ADDRESS}/books?query=${encodeURIComponent(query.query)}`
  );
  const books = await response.json();

  return books;
});
