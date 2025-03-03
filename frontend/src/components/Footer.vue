<template>
    <v-footer padless color="primary">
        <v-row justify="center" no-gutters>
            <v-btn class="mx-2" variant="text"> Impressum </v-btn>
            <v-btn class="mx-2" variant="text"> Datenschutzerklärung </v-btn>
            <v-col class="text-center mt-4" cols="12">
                {{ new Date().getFullYear() }} — <strong>Kantinenmanager Lebenshilfe Borna e.V.</strong>
            </v-col>
        </v-row>
    </v-footer>
</template>

<script setup>
//
</script>
