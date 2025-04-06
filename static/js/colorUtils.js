// Hilfsfunktion zum Generieren von Farben für Arbeitsorte
function getLocationColor(locationName) {
    // Einfache Hash-Funktion, um eine deterministische Farbe für jeden Ort zu erzeugen
    let hash = 0;
    for (let i = 0; i < locationName.length; i++) {
        hash = locationName.charCodeAt(i) + ((hash << 5) - hash);
    }
    
    // Stark kontrastierende Farben für bessere Unterscheidbarkeit
    // Diese Farben wurden speziell ausgewählt, um sich deutlich voneinander abzuheben
    // und trotzdem zum dunklen Design zu passen
    const colors = [
        '#FF3D00', // Leuchtendes Orange-Rot
        '#2979FF', // Kräftiges Blau
        '#00C853', // Sattes Grün
        '#AA00FF', // Leuchtendes Violett
        '#FFAB00', // Goldgelb
        '#00BFA5', // Türkis
        '#F50057', // Magenta
        '#3D5AFE', // Indigo
        '#76FF03', // Neon-Grün
        '#FF3D7F', // Pink
        '#00E5FF', // Cyan
        '#C6FF00', // Limette
        '#FF6D00', // Dunkel-Orange
        '#2196F3', // Material Blau
        '#FFC400', // Amber
        '#E040FB', // Purpur
        '#64DD17', // Helles Grün
        '#FF4081', // Rosa
        '#00B8D4', // Helles Cyan
        '#FFEA00', // Gelb
    ];
    
    // Index zwischen 0 und colors.length - 1 auswählen
    const colorIndex = Math.abs(hash) % colors.length;
    return colors[colorIndex];
}