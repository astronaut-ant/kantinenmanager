<template>
    <NavbarVerwaltung v-if="userrole == 'verwaltung'"/>
    <NavbarStandort v-else-if="userrole == 'standortleitung'"/>
    <NavbarGruppenleitung v-else-if="userrole == 'gruppenleitung'"/>
    <NavbarKueche v-else-if="userrole == 'kuechenpersonal'"/>
    <v-toolbar v-else class="bg-primary" flat app>
      <v-toolbar-title> </v-toolbar-title>
      <v-btn text class="mr-4" to="/login">Login <v-icon class="ms-2">mdi-login</v-icon></v-btn>
    </v-toolbar>
    <div>
        <v-card flat class="ml-4 text-blue-grey-darken-2">
            <v-card-title class="font-weight-black"> Impressum </v-card-title>
            <v-card-text class="ml-2">
                <p><strong>Lebenshilfe Borna e.V.</strong><br>
                Am Wilhelmschacht 1<br>
                04552 Borna</p>
            </v-card-text>
            <v-card-text class="ml-2">
                <p><strong>Vereinsregister:</strong> VR 10010</p>
                <p><strong>Registergericht:</strong> Amtsgericht Leipzig</p>
            </v-card-text>
            <v-card-text class="ml-2">
                <p><strong>Vertreten durch:</strong></p>
                <p>Frau Anja-Eugenie Lolies, 1. Vorsitzende</p>
                <p>Herr Hendrik Franke, 2. Vorsitzender</p>
            </v-card-text>
            <v-card-title class="font-weight-black"> Kontakt </v-card-title>
            <v-card-text class="ml-2"> 
                <p><strong>Telefon:</strong> 03433/ 20979-0</p>
                <p><strong>Telefax:</strong> 03433/ 20979-199</p>
                <p><strong>E-Mail:</strong> <a href="mailto:info@lebenshilfe-borna.de">info@lebenshilfe-borna.de</a></p>
            </v-card-text>
            <v-card-title class="font-weight-black"> Umsatzsteuer-ID </v-card-title>
            <v-card-text class="ml-2">
                <p>Umsatzsteuer-Identifikationsnummer gemäß § 27 a Umsatzsteuergesetz: DE141676333</p>
            </v-card-text>
            <v-card-title class="font-weight-black"> Verbraucher­streit­beilegung / Universal­schlichtungs­stelle </v-card-title>
            <v-card-text class="ml-2">
                <p>Wir sind nicht bereit oder verpflichtet, an Streitbeilegungsverfahren vor einer Verbraucherschlichtungsstelle teilzunehmen.</p>
            </v-card-text>
        </v-card>
    </div>

</template>

<script setup>
import NavbarGruppenleitung from "@/components/NavbarGruppenleitung.vue";
import NavbarKueche from "@/components/NavbarKueche.vue";
import NavbarStandort from "@/components/NavbarStandort.vue";
import NavbarVerwaltung from "@/components/NavbarVerwaltung.vue";
import { useAppStore } from "@/stores/app";
const appStore = useAppStore();

const userrole = appStore.userData.user_group;
</script>