<template>
  <div
    v-if="showModal"
    class="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full flex items-center justify-center"
    @click.self="showModal = false"
  >
    <!-- Modal -->
    <div class="p-5 border min-w-[50%] shadow-lg rounded-md bg-gray-100">
      <div class="text-xl font-bold text-center">{{ favBook }}</div>
      <div class="text-xl text-center mb-4">recomendations:</div>
      <div>
        <table v-if="recResult.length" class="w-full text-sm text-left">
            <thead class="text-xs bg-white">
                <tr>
                <th scope="col" class="py-3 px-6">Title</th>
                <th scope="col" class="py-3 px-6">Correlation</th>
                <th scope="col" class="py-3 px-6">Average rating</th>
                </tr>
            </thead>
            <tbody>
                <tr v-for="(book, index) in recResult" :key="index" class="bg-white border-b hover:bg-gray-200">
                <td class="py-4 px-6">{{ book.title }}</td>
                <td class="py-4 px-6">{{ book.corr }}</td>
                <td class="py-4 px-6">{{ book.avg_rating }}</td>
                </tr>
            </tbody>
        </table>
        <div v-else>
          <div class="text-center mt-2">No correlation found with selected title.</div>
        </div>
      </div>
      <div>
        <div class="flex justify-end">
          <button
            class="bg-red-500 text-white hover:bg-red-700 py-2 px-4 border border-black rounded shadow"
            @click="showModal = false"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { list } from 'postcss';

const props = defineProps({
  favBook: String,
  showModal: Boolean,
  recResult: list,
});
/*
const recResult = ref([]);

// Function to fetch recommendations
async function fetchRecommendations(favBook) {
    console.log(`fetching ${favBook}`);
  const { data, pending, error } = await useFetch(`/api/recommend`, {
    params: { book: favBook },
    // This option makes sure the fetch is executed immediately,
    // suitable for function calls inside watch or lifecycle hooks.
    immediate: true,
  });
  if (!error.value) {
    recResult.value = data.value || [];
  } else {
    console.error(error.value);
    recResult.value = [];
  }
}

// Watch for changes in showModal and favBook
watch(
  [() => props.showModal, () => props.favBook],
  ([newShowModal, newFavBook], [oldShowModal, oldFavBook]) => {
    if (newShowModal && newFavBook && newFavBook !== oldFavBook) {
      fetchRecommendations(newFavBook);
    }
    if (!newShowModal && newShowModal !== oldShowModal) {
      recResult.value = [];
    }
  },
  { immediate: true }
);
*/
</script>

<style scoped>
table td,
table th {
  border: 1px solid #d1d5db;
  padding: 8px;
}
</style>
