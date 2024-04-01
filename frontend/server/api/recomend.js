export default defineEventHandler(async (event) => {
  const query = getQuery(event);

  const requestOptions = {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ book: query.book }),
  };

  const response = await fetch(
    `${process.env.BE_ADDRESS}/recommend`,
    requestOptions
  );
  const books = await response.json();

  console.log(books);

  return books;
});
