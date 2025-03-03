<template>
    <v-footer padless class="footer">
        <v-row justify="center" no-gutters>
            <v-btn
                v-for="link in links"
                :key="link"
                class="mx-2"
                variant="text"
            >
                {{ link }}
            </v-btn>
            <v-col class="text-center mt-4" cols="12">
                {{ new Date().getFullYear() }} — <strong>Kantinenmanager Lebenshilfe Borna e.V.</strong>
            </v-col>
        </v-row>
    </v-footer>
</template>

<script setup>
const links = ["Impressum", "Datenschutz", "AGB"];

</script>

<style>
.footer {
  height: 64px;
}
</style>