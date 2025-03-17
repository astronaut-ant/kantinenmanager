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
            <v-card-title class="font-weight-black"> Datenschutzerklärung </v-card-title>
            <v-card-text class="ml-2">
                <p>Mit der folgenden Datenschutzerklärung möchten wir Sie darüber aufklären, welche Arten Ihrer personenbezogenen Daten (nachfolgend auch kurz als "Daten" bezeichnet) wir zu welchen Zwecken und in welchem Umfang im Rahmen der Bereitstellung unserer Applikation verarbeiten.</p>
                <p>Die verwendeten Begriffe sind nicht geschlechtsspezifisch.</p>
                <p><strong>Stand:</strong> 17. März 2025</p>
            </v-card-text>

            <v-card-title class="font-weight-black"> Inhaltsübersicht </v-card-title>
            <v-card-text class="ml-2">
                <ul class="index">
                    <li><a class="index-link" href="#m3">Verantwortlicher</a></li>
                    <li><a class="index-link" href="#m11">Kontakt Datenschutzbeauftragter</a></li>
                    <li><a class="index-link" href="#mOverview">Übersicht der Verarbeitungen</a></li>
                    <li><a class="index-link" href="#m2427">Maßgebliche Rechtsgrundlagen</a></li>
                    <li><a class="index-link" href="#m225">Bereitstellung des Onlineangebots und Webhosting</a></li>
                    <li><a class="index-link" href="#m134">Einsatz von Cookies</a></li>
                    <li><a class="index-link" href="#m15">Änderung und Aktualisierung</a></li>
                </ul>
            </v-card-text>

            <v-card-title class="font-weight-black" id="m3"> Verantwortlicher </v-card-title>
            <v-card-text class="ml-2">
                <p><strong>Lebenshilfe Borna e.V.</strong><br>
                Am Wilhelmschacht 1<br>
                04552 Borna<br><br>
                E-Mail: <a href="mailto:info@lebenshilfe-borna.de">info@lebenshilfe-borna.de</a><br>
                Telefon: 03433/2769-0<br>
                Fax: 03433/2769-35</p>
            </v-card-text>

            <v-card-title class="font-weight-black" id="m11"> Kontakt Datenschutzbeauftragter </v-card-title>
            <v-card-text class="ml-2">
                <p>Herr Andreas Nanos<br><br>
                DID Dresdner Institut für Datenschutz<br>
                Hospitalstr. 4<br>
                01097 Dresden<br><br>
                E-Mail: <a href="mailto:a.nanos@dids.de">a.nanos@dids.de</a><br>
                Telefon: 0351 / 655 772-0<br>
                Fax: 0351 / 655 772 22</p>
            </v-card-text>

            <v-card-title class="font-weight-black" id="mOverview"> Übersicht der Verarbeitungen </v-card-title>
            <v-card-text class="ml-2">
                <p>Die nachfolgende Übersicht fasst die Arten der verarbeiteten Daten und die Zwecke ihrer Verarbeitung zusammen und verweist auf die betroffenen Personen. </p>
                <p> <br></p>
                <h3>Arten der verarbeiteten Daten</h3>
                <ul class="ml-4">
                    <li>Bestandsdaten.</li>
                    <li>Kontaktdaten.</li>
                    <li>Inhaltsdaten.</li>
                    <li>Nutzungsdaten.</li>
                    <li>Meta-, Kommunikations- und Verfahrensdaten.</li>
                    <li>Protokolldaten.</li>
                </ul>
                <p> <br></p>
                <h3>Kategorien betroffener Personen</h3>
                <ul class="ml-4">
                    <li>Kommunikationspartner.</li>
                    <li>Nutzer.</li>
                </ul>
                <p> <br></p>
                <h3>Zwecke der Verarbeitung</h3>
                <ul class="ml-4">
                    <li>Kommunikation.</li>
                    <li>Sicherheitsmaßnahmen.</li>
                    <li>Organisations- und Verwaltungsverfahren.</li>
                    <li>Feedback.</li>
                    <li>Bereitstellung unseres Onlineangebotes und Nutzerfreundlichkeit.</li>
                    <li>Informationstechnische Infrastruktur.</li>
                </ul>
            </v-card-text>

            <v-card-title class="font-weight-black" id="m2427"> Maßgebliche Rechtsgrundlagen </v-card-title>
            <v-card-text class="ml-2">
                <p><strong>Maßgebliche Rechtsgrundlagen nach der DSGVO: </strong>Im Folgenden erhalten Sie eine Übersicht der Rechtsgrundlagen der DSGVO, auf deren Basis wir personenbezogene Daten verarbeiten. Bitte nehmen Sie zur Kenntnis, dass neben den Regelungen der DSGVO nationale Datenschutzvorgaben in Ihrem bzw. unserem Wohn- oder Sitzland gelten können. Sollten ferner im Einzelfall speziellere Rechtsgrundlagen maßgeblich sein, teilen wir Ihnen diese in der Datenschutzerklärung mit.</p>
                <ul class="ml-4">
                    <li ><strong>Berechtigte Interessen (Art. 6 Abs. 1 S. 1 lit. f) DSGVO)</strong> - die Verarbeitung ist zur Wahrung der berechtigten Interessen des Verantwortlichen oder eines Dritten notwendig, vorausgesetzt, dass die Interessen, Grundrechte und Grundfreiheiten der betroffenen Person, die den Schutz personenbezogener Daten verlangen, nicht überwiegen.</li>
                </ul>
                <p> <br></p>
                <p><strong>Nationale Datenschutzregelungen in Deutschland: </strong>Zusätzlich zu den Datenschutzregelungen der DSGVO gelten nationale Regelungen zum Datenschutz in Deutschland. Hierzu gehört insbesondere das Gesetz zum Schutz vor Missbrauch personenbezogener Daten bei der Datenverarbeitung (Bundesdatenschutzgesetz – BDSG). Das BDSG enthält insbesondere Spezialregelungen zum Recht auf Auskunft, zum Recht auf Löschung, zum Widerspruchsrecht, zur Verarbeitung besonderer Kategorien personenbezogener Daten, zur Verarbeitung für andere Zwecke und zur Übermittlung sowie automatisierten Entscheidungsfindung im Einzelfall einschließlich Profiling. Ferner können Landesdatenschutzgesetze der einzelnen Bundesländer zur Anwendung gelangen.</p>
            </v-card-text>

            <v-card-title class="font-weight-black" id="m225"> Bereitstellung des Onlineangebots und Webhosting </v-card-title>
            <v-card-text class="ml-2">
                <p>Wir verarbeiten die Daten der Nutzer, um ihnen unsere Online-Dienste zur Verfügung stellen zu können. Zu diesem Zweck verarbeiten wir die IP-Adresse des Nutzers, die notwendig ist, um die Inhalte und Funktionen unserer Online-Dienste an den Browser oder das Endgerät der Nutzer zu übermitteln.</p>
                <ul class="m-elements ml-4" >
                    <li><strong>Verarbeitete Datenarten:</strong> Nutzungsdaten (z. B. Seitenaufrufe und Verweildauer, Klickpfade, Nutzungsintensität und -frequenz, verwendete Gerätetypen und Betriebssysteme, Interaktionen mit Inhalten und Funktionen); Meta-, Kommunikations- und Verfahrensdaten (z. B. IP-Adressen, Zeitangaben, Identifikationsnummern, beteiligte Personen). Protokolldaten (z. B. Logfiles betreffend Logins oder den Abruf von Daten oder Zugriffszeiten.).</li>
                    <li><strong>Betroffene Personen:</strong> Nutzer (z. B. Webseitenbesucher, Nutzer von Onlinediensten).</li>
                    <li><strong>Zwecke der Verarbeitung:</strong> Bereitstellung unseres Onlineangebotes und Nutzerfreundlichkeit; Informationstechnische Infrastruktur (Betrieb und Bereitstellung von Informationssystemen und technischen Geräten (Computer, Server etc.)). Sicherheitsmaßnahmen.</li>
                    <li><strong>Aufbewahrung und Löschung:</strong> Löschung entsprechend Angaben im Abschnitt "Allgemeine Informationen zur Datenspeicherung und Löschung".</li>
                    <li><strong>Rechtsgrundlagen:</strong> Berechtigte Interessen (Art. 6 Abs. 1 S. 1 lit. f) DSGVO).</li>
                </ul>
                <p> <br></p>
                <p><strong>Weitere Hinweise zu Verarbeitungsprozessen, Verfahren und Diensten:</strong></p>
                <ul class="m-elements ml-4">
                    <li><strong>Bereitstellung Onlineangebot auf eigener/ dedizierter Serverhardware: </strong>Für die Bereitstellung unseres Onlineangebotes nutzen wir von uns betriebene Serverhardware sowie den damit verbundenen Speicherplatz, die Rechenkapazität und die Software; <span class=""><strong>Rechtsgrundlagen:</strong> Berechtigte Interessen (Art. 6 Abs. 1 S. 1 lit. f) DSGVO).</span></li>
                    <li><strong>Erhebung von Zugriffsdaten und Logfiles: </strong>Der Zugriff auf unser Onlineangebot wird in Form von sogenannten "Server-Logfiles" protokolliert. Zu den Serverlogfiles können die Adresse und der Name der abgerufenen Webseiten und Dateien, Datum und Uhrzeit des Abrufs, übertragene Datenmengen, Meldung über erfolgreichen Abruf, Browsertyp nebst Version, das Betriebssystem des Nutzers, Referrer URL (die zuvor besuchte Seite) und im Regelfall IP-Adressen und der anfragende Provider gehören. Die Serverlogfiles können zum einen zu Sicherheitszwecken eingesetzt werden, z. B. um eine Überlastung der Server zu vermeiden (insbesondere im Fall von missbräuchlichen Angriffen, sogenannten DDoS-Attacken), und zum anderen, um die Auslastung der Server und ihre Stabilität sicherzustellen; 
                    <span class=""><strong>Rechtsgrundlagen:</strong> Berechtigte Interessen (Art. 6 Abs. 1 S. 1 lit. f) DSGVO). </span><strong>Löschung von Daten:</strong> Logfile-Informationen werden für die Dauer von maximal 30 Tagen gespeichert und danach gelöscht oder anonymisiert. Daten, deren weitere Aufbewahrung zu Beweiszwecken erforderlich ist, sind bis zur endgültigen Klärung des jeweiligen Vorfalls von der Löschung ausgenommen.</li>
                </ul>
            </v-card-text>

            <v-card-title class="font-weight-black" id="m134"> Einsatz von Cookies </v-card-title>
            <v-card-text class="ml-2">
                <p>Unter dem Begriff „Cookies" werden Funktionen, die Informationen auf Endgeräten der Nutzer speichern und aus ihnen auslesen, verstanden. Cookies können ferner in Bezug auf unterschiedliche Anliegen Einsatz finden, etwa zu Zwecken der Funktionsfähigkeit, der Sicherheit und des Komforts von Onlineangeboten sowie der Erstellung von Analysen der Besucherströme. Wir verwenden Cookies gemäß den gesetzlichen Vorschriften. Dazu holen wir, wenn erforderlich, vorab die Zustimmung der Nutzer ein. Ist eine Zustimmung nicht notwendig, setzen wir auf unsere berechtigten Interessen. Dies gilt, wenn das Speichern und Auslesen von Informationen unerlässlich ist, um ausdrücklich angeforderte Inhalte und Funktionen bereitstellen zu können. Dazu zählen etwa die Speicherung von Einstellungen sowie die Sicherstellung der Funktionalität und Sicherheit unseres Onlineangebots. Die Einwilligung kann jederzeit widerrufen werden. Wir informieren klar über deren Umfang und welche Cookies genutzt werden.</p>
                <p> <br></p>
                <p><strong>Hinweise zu datenschutzrechtlichen Rechtsgrundlagen: </strong>Ob wir personenbezogene Daten mithilfe von Cookies verarbeiten, hängt von einer Einwilligung ab. Liegt eine Einwilligung vor, dient sie als Rechtsgrundlage. Ohne Einwilligung stützen wir uns auf unsere berechtigten Interessen, die vorstehend in diesem Abschnitt und im Kontext der jeweiligen Dienste und Verfahren erläutert sind.</p>
                <p> <br></p>
                <p><strong>Speicherdauer: </strong>Im Hinblick auf die Speicherdauer werden die folgenden Arten von Cookies unterschieden:</p>
                <ul class="ml-4">
                    <li><strong>Temporäre Cookies (auch: Session- oder Sitzungscookies):</strong> Temporäre Cookies werden spätestens gelöscht, nachdem ein Nutzer ein Onlineangebot verlassen und sein Endgerät (z. B. Browser oder mobile Applikation) geschlossen hat.</li>
                    <li><strong>Permanente Cookies:</strong> Permanente Cookies bleiben auch nach dem Schließen des Endgeräts gespeichert. So können beispielsweise der Log-in-Status gespeichert und bevorzugte Inhalte direkt angezeigt werden, wenn der Nutzer eine Website erneut besucht. Ebenso können die mithilfe von Cookies erhobenen Nutzerdaten zur Reichweitenmessung Verwendung finden. Sofern wir Nutzern keine expliziten Angaben zur Art und Speicherdauer von Cookies mitteilen (z. B. im Rahmen der Einholung der Einwilligung), sollten sie davon ausgehen, dass diese permanent sind und die Speicherdauer bis zu zwei Jahre betragen kann.</li>
                </ul>
                <p> <br></p>
                <p><strong>Allgemeine Hinweise zum Widerruf und Widerspruch (Opt-out): </strong>Nutzer können die von ihnen abgegebenen Einwilligungen jederzeit widerrufen und zudem einen Widerspruch gegen die Verarbeitung entsprechend den gesetzlichen Vorgaben, auch mittels der Privatsphäre-Einstellungen ihres Browsers, erklären.</p>
                <ul class="m-elements  ml-4">
                    <li><strong>Verarbeitete Datenarten:</strong> Meta-, Kommunikations- und Verfahrensdaten (z. B. IP-Adressen, Zeitangaben, Identifikationsnummern, beteiligte Personen).</li>
                    <li><strong>Betroffene Personen:</strong> Nutzer (z. B. Webseitenbesucher, Nutzer von Onlinediensten).</li>
                    <li><strong>Rechtsgrundlagen:</strong> Berechtigte Interessen (Art. 6 Abs. 1 S. 1 lit. f) DSGVO).</li>
                </ul>
            </v-card-text>

            <v-card-title class="font-weight-black" id="m15"> Änderung und Aktualisierung </v-card-title>
            <v-card-text class="ml-2">
                <p>Wir bitten Sie, sich regelmäßig über den Inhalt unserer Datenschutzerklärung zu informieren. Wir passen die Datenschutzerklärung an, sobald die Änderungen der von uns durchgeführten Datenverarbeitungen dies erforderlich machen. Wir informieren Sie, sobald durch die Änderungen eine Mitwirkungshandlung Ihrerseits (z. B. Einwilligung) oder eine sonstige individuelle Benachrichtigung erforderlich wird.</p>
                <p>Sofern wir in dieser Datenschutzerklärung Adressen und Kontaktinformationen von Unternehmen und Organisationen angeben, bitten wir zu beachten, dass die Adressen sich über die Zeit ändern können und bitten die Angaben vor Kontaktaufnahme zu prüfen.</p>
            </v-card-text>

            <v-card-text class="ml-2">
                <p class="seal"><a href="https://datenschutz-generator.de/" title="Rechtstext von Dr. Schwenke - für weitere Informationen bitte anklicken." target="_blank" rel="noopener noreferrer nofollow">Erstellt mit Datenschutz-Generator.de von Dr. Thomas Schwenke</a></p>
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