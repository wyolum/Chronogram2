/* DateStrings.cpp
 * Definitions for date strings for use with the Time library
 *
 * No memory is consumed in the sketch if your code does not call any of the string methods
 * You can change the text of the strings, make sure the short strings are each exactly 3 characters 
 * the long strings can be any length up to the constant dt_MAX_STRING_LEN defined in Time.h
 * 
 */
 
#include <avr/pgmspace.h> 
#include "Time.h"
 
// the short strings for each day or month must be exactly dt_SHORT_STR_LEN
#define dt_SHORT_STR_LEN  3 // the length of short strings

static char buffer[dt_MAX_STRING_LEN+1];  // must be big enough for longest string and the terminating null

char const monthStr1[] PROGMEM = "January";
char const monthStr2[] PROGMEM = "February";
char const monthStr3[] PROGMEM = "March";
char const monthStr4[] PROGMEM = "April";
char const monthStr5[] PROGMEM = "May";
char const monthStr6[] PROGMEM = "June";
char const monthStr7[] PROGMEM = "July";
char const monthStr8[] PROGMEM = "August";
char const monthStr9[] PROGMEM = "September";
char const monthStr10[] PROGMEM = "October";
char const monthStr11[] PROGMEM = "November";
char const monthStr12[] PROGMEM = "December";

PGM_P const monthNames_P[] PROGMEM = 
{
    "",monthStr1,monthStr2,monthStr3,monthStr4,monthStr5,monthStr6,
	monthStr7,monthStr8,monthStr9,monthStr10,monthStr11,monthStr12
};

char const monthShortNames_P[] PROGMEM = "ErrJanFebMarAprMayJunJulAugSepOctNovDec";

char const dayStr0[] PROGMEM = "Err";
char const dayStr1[] PROGMEM = "Sunday";
char const dayStr2[] PROGMEM = "Monday";
char const dayStr3[] PROGMEM = "Tuesday";
char const dayStr4[] PROGMEM = "Wednesday";
char const dayStr5[] PROGMEM = "Thursday";
char const dayStr6[] PROGMEM = "Friday";
char const dayStr7[] PROGMEM = "Saturday";

PGM_P const dayNames_P[] PROGMEM = { dayStr0,dayStr1,dayStr2,dayStr3,dayStr4,dayStr5,dayStr6,dayStr7};
char const dayShortNames_P[] PROGMEM = "ErrSunMonTueWedThrFriSat";

/* functions to return date strings */

char* monthStr(uint8_t month)
{
    strcpy_P(buffer, (PGM_P)pgm_read_word(&(monthNames_P[month])));
	return buffer;
}

char* monthShortStr(uint8_t month)
{
   for (int i=0; i < dt_SHORT_STR_LEN; i++)      
      buffer[i] = pgm_read_byte(&(monthShortNames_P[i+ (month*dt_SHORT_STR_LEN)]));  
   buffer[dt_SHORT_STR_LEN] = 0;
   return buffer;
}

char* dayStr(uint8_t day) 
{
   strcpy_P(buffer, (PGM_P)pgm_read_word(&(dayNames_P[day])));
   return buffer;
}

char* dayShortStr(uint8_t day) 
{
   uint8_t index = day*dt_SHORT_STR_LEN;
   for (int i=0; i < dt_SHORT_STR_LEN; i++)      
      buffer[i] = pgm_read_byte(&(dayShortNames_P[index + i]));  
   buffer[dt_SHORT_STR_LEN] = 0; 
   return buffer;
}
