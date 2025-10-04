class Utils {
    static convertToDate(dateString: string): Date {
        // Extract day, month, year from DDMMYYYY format
        const day = dateString.substring(0, 2);
        const month = dateString.substring(2, 4);
        const year = dateString.substring(4, 8);
        
        // Create Date object (month is 0-indexed)
        return new Date(parseInt(year), parseInt(month) - 1, parseInt(day));
    }
}

export default Utils;