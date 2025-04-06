/**
 * Funktion zur konsistenten Generierung von Farben basierend auf dem Namen eines Arbeitsortes
 */
function getLocationColor(locationName) {
    // Predefinierten Farben im Stil des Designs (verschiedene Farbtöne, die gut zum Design passen)
    const colors = [
        '#7B1CD7', // primary-600
        '#11A3D4', // accent-500
        '#6C18BB', // primary-700
        '#0F8FB8', // accent-600
        '#9F4CF5', // primary-400
        '#3EB3DB', // accent-400
        '#8A20F2', // primary-500
        '#0D7A9D', // accent-700
        '#B378F7', // primary-300
        '#0B6581'  // accent-800
    ];
    
    // Einfache Hash-Funktion für den Location-Namen
    let hash = 0;
    for (let i = 0; i < locationName.length; i++) {
        hash = locationName.charCodeAt(i) + ((hash << 5) - hash);
    }
    
    // Sicherstellen, dass der Hash positiv ist
    hash = Math.abs(hash);
    
    // Index in das Farb-Array umwandeln
    const colorIndex = hash % colors.length;
    
    return colors[colorIndex];
}
