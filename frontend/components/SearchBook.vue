<template>
  <div class="flex flex-col h-screen justify-center">
    <div
      class="fixed top-0 left-0 right-0 z-10 bg-white p-4 flex justify-center"
    >
      <input
        class="w-full max-w-4xl mx-auto text-lg p-4 border-2 border-gray-200 rounded-lg focus:outline-none focus:border-blue-500 transition-colors"
        type="text"
        placeholder="Search Book"
        @input="debounceSearch"
        v-model="searchInput"
      />
      <div v-if="pending" class="text-center mt-2">Loading...</div>
    </div>
    <div class="pt-24 overflow-auto">
      <ul v-if="searchResults.length" class="results max-w-4xl mx-auto">
        <li
          v-for="(book, index) in searchResults"
          :key="index"
          class="p-2 hover:bg-gray-100 cursor-pointer truncate"
          @click="selectBook(book)"
        >
          {{ book }}
        </li>
      </ul>
    </div>
  </div>
  <div>
    <lazy-Recomendation :favBook="favBook" :showModal="showModal" :recResult="recResult" />
  </div>
</template>

<style scoped>
.results::-webkit-scrollbar {
  display: none;
}
.results {
  -ms-overflow-style: none;
  scrollbar-width: none;
}
</style>

<script setup>
const searchInput = ref("");
const searchResults = ref([]);
const pending = ref(false);

const favBook = ref("");
const showModal = ref(false);
const recResult = ref([]);

const fetchBooks = async (query) => {
  pending.value = true;
  searchResults.value = await $fetch("/api/books", {
    params: { query },
  }).finally(() => (pending.value = false));
};

let timeout;
const debounceSearch = () => {
  clearTimeout(timeout);
  timeout = setTimeout(() => {
    if (!searchInput.value) {
      searchResults.value = [];
    }
    if (searchInput.value.length > 2) {
      fetchBooks(searchInput.value);
    }
  }, 500);
};

// Example function to handle book selection
const selectBook = (book) => {
  console.log(`${book} clicked`);
  favBook.value = book;
  showModal.value = false;
  recResult.value = [];
  fetchRecomendations(book);
  nextTick(() => {
    showModal.value = true;
  });
};

const fetchRecomendations = async (book) => {
  pending.value = true;
  recResult.value = await $fetch("/api/recomend", {
    params: { book },
  });
};
</script>
