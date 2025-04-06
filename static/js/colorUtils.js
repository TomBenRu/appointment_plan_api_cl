// Hilfsfunktion zum Generieren von Farben für Arbeitsorte
function getLocationColor(locationName) {
    // Einfache Hash-Funktion, um eine deterministische Farbe für jeden Ort zu erzeugen
    let hash = 0;
    for (let i = 0; i < locationName.length; i++) {
        hash = locationName.charCodeAt(i) + ((hash << 5) - hash);
    }
    
    // Harmonische Farben, die zum dunklen Design passen
    // Gedämpfte, aber klar unterscheidbare Farben in mittlerer Sättigung
    const colors = [
        '#8A20F2', // primary-500 (Original-Lila)
        '#11A3D4', // accent-500 (Original-Blau)
        '#9C27B0', // Magenta-Lila
        '#0D7A9D', // accent-700 (Dunkleres Blau)
        '#6C18BB', // primary-700 (Dunkleres Lila)
        '#3949AB', // Dunkleres Blau
        '#1E88E5', // Mittleres Blau
        '#5E35B1', // Indigo
        '#039BE5', // Helleres Blau
        '#00ACC1', // Türkis
        '#00897B', // Grün-Türkis
        '#43A047', // Gedämpftes Grün
        '#C0CA33', // Blassgelb
        '#FDD835', // Gedämpftes Gelb
        '#FFB300', // Goldgelb
        '#FB8C00', // Gedämpftes Orange
        '#F4511E', // Terrakotta
        '#7CB342', // Olivgrün
        '#E53935', // Gedämpftes Rot
        '#D81B60', // Gedämpftes Pink
        '#8E24AA', // Lila-Pink
        '#5C6BC0', // Graublau
        '#26A69A', // Meeresblau
        '#66BB6A', // Pastellgrün
    ];
    
    // Index zwischen 0 und colors.length - 1 auswählen
    const colorIndex = Math.abs(hash) % colors.length;
    return colors[colorIndex];
}