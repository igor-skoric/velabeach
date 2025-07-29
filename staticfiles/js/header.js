 const { createApp, ref, onMounted, onBeforeUnmount, reactive  } = Vue;

     const header = createApp({
       setup() {
         const user = reactive(window.user || {}) ;
         const screenWidth = ref(window.innerWidth);
         const isOpen = ref(false);

         const updateWidth = () => {
            screenWidth.value = window.innerWidth;
         };

         onMounted(() => {
            window.addEventListener('resize', updateWidth);
            if (screenWidth.value > 1240){
                isOpen.value = ref(true);
            }
         });

         onBeforeUnmount(() => {
            window.removeEventListener('resize', updateWidth);
         });

         function toggleMenu() {
           isOpen.value = !isOpen.value;
         }

         return { isOpen, toggleMenu, screenWidth, user };
       }
     });

     header.config.compilerOptions.delimiters = ['[[', ']]'];
     header.mount("#vue-navbar");