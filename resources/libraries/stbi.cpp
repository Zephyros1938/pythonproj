#include "stb/stb_image.h"
#include <iostream>
#include <ostream>

using namespace std;

int main() {
  cout << "Loaded" << std::endl;
  return 0;
}

unsigned char *stbi_load_gif_from_memory(const stbi_uc *buffer, int len,
                                         int **delays, int *x, int *y, int *z,
                                         int *comp, int req_comp) {
  return stbi_load_gif_from_memory(buffer, len, delays, x, y, z, comp,
                                   req_comp);
}

unsigned char *stbi_load_from_memory(const stbi_uc *buffer, int len, int *x,
                                     int *y, int *channels_in_file,
                                     int desired_channels) {
  return stbi_load_from_memory(buffer, len, x, y, channels_in_file,
                               desired_channels);
}

unsigned char *stbi_load(const char *filename, int *x, int *y,
                         int *channels_in_file, int desired_channels) {
  return stbi_load(filename, x, y, channels_in_file, desired_channels);
}

