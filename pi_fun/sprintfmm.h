#include <PString.h>

template <typename T>
void numprint(T val, int width, bool rightjustify = true) {
  char buff[width];
  PString str(buff, width);
  str.print(val);
  int room = str.capacity() - str.length();
  if (room) {
    if (rightjustify) {
      for (int i=0; i<room; i++) { Serial.print(F(" ")); }
      Serial.print(str);
      }
    else {
      Serial.print(str);
      for (int i=0; i<room; i++) { Serial.print(F(" ")); }
      }
    }
  }
