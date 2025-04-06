// Hilfsfunktion zum Generieren von Farben für Arbeitsorte
function getLocationColor(locationName) {
    // Einfache Hash-Funktion, um eine deterministische Farbe für jeden Ort zu erzeugen
    let hash = 0;
    for (let i = 0; i < locationName.length; i++) {
        hash = locationName.charCodeAt(i) + ((hash << 5) - hash);
    }
    
    // Wir verwenden ein begrenztes Set von Farben, die gut zusammenpassen
    const colors = [
        '#8A20F2', // primary-500
        '#6C18BB', // primary-700
        '#5D14A0', // primary-800
        '#11A3D4', // accent-500
        '#0D7A9D', // accent-700
        '#095166', // accent-900
        '#F67280', // Ein Rosa-Ton
        '#70C1B3', // Ein Türkis-Ton
        '#FFE066', // Ein Gelb-Ton
        '#247BA0', // Ein Blau-Ton
        '#FF1654', // Ein Rot-Ton
    ];
    
    // Index zwischen 0 und colors.length - 1 auswählen
    const colorIndex = Math.abs(hash) % colors.length;
    return colors[colorIndex];
}