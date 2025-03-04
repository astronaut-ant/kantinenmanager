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
        <v-card flat class="ml-4">
            <v-card-title class="font-weight-black"> Datenschutzerklärung </v-card-title>
            <v-card-text class="ml-2">
                <p>Mit der folgenden Datenschutzerklärung möchten wir Sie darüber aufklären, welche Arten Ihrer personenbezogenen Daten (nachfolgend auch kurz als "Daten" bezeichnet) wir zu welchen Zwecken und in welchem Umfang im Rahmen der Bereitstellung unserer Applikation verarbeiten.</p>
                <p>Die verwendeten Begriffe sind nicht geschlechtsspezifisch.</p>
                <p><strong>Stand:</strong> 4. März 2025</p>
            </v-card-text>
            
            <v-card-title class="font-weight-black"> Verantwortlicher </v-card-title>
            <v-card-text class="ml-2">
                <p><strong>Lebenshilfe Borna e.V.</strong><br>
                Am Wilhelmschacht 1<br>
                04552 Borna</p>
                <p><strong>E-Mail:</strong> <a href="mailto:info@lebenshilfe-borna.de">info@lebenshilfe-borna.de</a></p>
                <p><strong>Telefon:</strong> 03433/2769-0</p>
                <p><strong>Fax:</strong> 03433/2769-35</p>
            </v-card-text>
            
            <v-card-title class="font-weight-black"> Kontakt Datenschutzbeauftragter </v-card-title>
            <v-card-text class="ml-2">
                <p><strong>Herr Andreas Nanos</strong></p>
                <p>DID Dresdner Institut für Datenschutz<br>
                Hospitalstr. 4<br>
                01097 Dresden</p>
                <p><strong>E-Mail:</strong> <a href="mailto:a.nanos@dids.de">a.nanos@dids.de</a></p>
                <p><strong>Telefon:</strong> 0351 / 655 772-0</p>
                <p><strong>Fax:</strong> 0351 / 655 772 22</p>
            </v-card-text>
            
            <v-card-title class="font-weight-black"> Sicherheitsmaßnahmen </v-card-title>
            <v-card-text class="ml-2">
                <p>Wir treffen nach Maßgabe der gesetzlichen Vorgaben geeignete technische und organisatorische Maßnahmen, um ein dem Risiko angemessenes Schutzniveau zu gewährleisten.</p>
                <p>Hierzu gehören insbesondere:</p>
                <ul>
                    <li>Schutz der Vertraulichkeit, Integrität und Verfügbarkeit von Daten</li>
                    <li>Zugriffs- und Weitergabekontrollen</li>
                    <li>Verschlüsselte Datenübertragung (TLS/SSL)</li>
                </ul>
            </v-card-text>
            
            <v-card-title class="font-weight-black"> Rechte der betroffenen Personen </v-card-title>
            <v-card-text class="ml-2">
                <p>Nach der DSGVO haben Sie unter anderem folgende Rechte:</p>
                <ul>
                    <li>Widerspruchsrecht</li>
                    <li>Widerrufsrecht bei Einwilligungen</li>
                    <li>Auskunftsrecht</li>
                    <li>Recht auf Berichtigung und Löschung</li>
                    <li>Recht auf Datenübertragbarkeit</li>
                    <li>Beschwerderecht bei einer Aufsichtsbehörde</li>
                </ul>
            </v-card-text>
            
            <v-card-title class="font-weight-black"> Bereitstellung des Onlineangebots und Webhosting </v-card-title>
            <v-card-text class="ml-2">
                <p>Wir verarbeiten die Daten der Nutzer, um ihnen unsere Online-Dienste zur Verfügung stellen zu können.</p>
                <p><strong>Verarbeitete Datenarten:</strong></p>
                <ul>
                    <li>Nutzungsdaten</li>
                    <li>Meta-, Kommunikations- und Verfahrensdaten</li>
                    <li>Protokolldaten</li>
                </ul>
            </v-card-text>
            
            <v-card-title class="font-weight-black"> Änderung und Aktualisierung </v-card-title>
            <v-card-text class="ml-2">
                <p>Wir bitten Sie, sich regelmäßig über den Inhalt unserer Datenschutzerklärung zu informieren. Wir passen die Datenschutzerklärung an, sobald Änderungen der Datenverarbeitung dies erforderlich machen.</p>
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