/*
Copyright (c) 2012 Ben Croston
Modified by Eric PTAK

Permission is hereby granted, free of charge, to any person obtaining a copy of
this software and associated documentation files (the "Software"), to deal in
the Software without restriction, including without limitation the rights to
use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
of the Software, and to permit persons to whom the Software is furnished to do
so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
*/

#include "Python.h"
#include "gpio.h"
#include "cpuinfo.h"

static PyObject *_SetupException;
static PyObject *_InvalidDirectionException;
static PyObject *_InvalidChannelException;
static PyObject *_InvalidPullException;

static PyObject *_gpioCount;


static PyObject *_low;
static PyObject *_high;

static PyObject *_input;
static PyObject *_output;
static PyObject *_alt0;
static PyObject *_alt1;
static PyObject *_alt2;
static PyObject *_alt3;
static PyObject *_alt4;
static PyObject *_alt5;

static PyObject *_pud_off;
static PyObject *_pud_up;
static PyObject *_pud_down;

static PyObject *_board_revision;

static char* FUNCTIONS[] = {"IN", "OUT", "ALT5", "ALT4", "ALT0", "ALT1", "ALT2", "ALT3"};


// setup function run on import of the RPi.GPIO module
static int module_setup(void)
{
   int result;

   result = setup();
   if (result == SETUP_DEVMEM_FAIL)
   {
      PyErr_SetString(_SetupException, "No access to /dev/mem.  Try running as root!");
      return SETUP_DEVMEM_FAIL;
   } else if (result == SETUP_MALLOC_FAIL) {
      PyErr_NoMemory();
      return SETUP_MALLOC_FAIL;
   } else if (result == SETUP_MMAP_FAIL) {
      PyErr_SetString(_SetupException, "Mmap failed on module import");
      return SETUP_MALLOC_FAIL;
   } else { // result == SETUP_OK
      return SETUP_OK;
   }
}

// python function setup(channel, direction, pull_up_down=PUD_OFF)
static PyObject *py_set_function(PyObject *self, PyObject *args, PyObject *kwargs)
{
   int channel, direction;
   int pud = PUD_OFF;
   static char *kwlist[] = {"channel", "direction", "pull_up_down", NULL};
   
   if (!PyArg_ParseTupleAndKeywords(args, kwargs, "ii|i", kwlist, &channel, &direction, &pud))
      return NULL;

   if (direction != INPUT && direction != OUTPUT)
   {
      PyErr_SetString(_InvalidDirectionException, "An invalid direction was passed to setup()");
      return NULL;
   }

   if (direction == OUTPUT)
      pud = PUD_OFF;

   if (pud != PUD_OFF && pud != PUD_DOWN && pud != PUD_UP)
   {
      PyErr_SetString(_InvalidPullException, "Invalid value for pull_up_down - should be either PUD_OFF, PUD_UP or PUD_DOWN");
      return NULL;
   }

   if (channel < 0 || channel > 53)
   {
      PyErr_SetString(_InvalidChannelException, "The channel sent is invalid on a Raspberry Pi");
      return NULL;
   }

   set_function(channel, direction, pud);

   Py_INCREF(Py_None);
   return Py_None;
}

// python function output(channel, value)
static PyObject *py_output(PyObject *self, PyObject *args, PyObject *kwargs)
{
   int channel, value;
   static char *kwlist[] = {"channel", "value", NULL};

   if (!PyArg_ParseTupleAndKeywords(args, kwargs, "ii", kwlist, &channel, &value))
      return NULL;

   if (channel < 0 || channel >= GPIO_COUNT)
   {
      PyErr_SetString(_InvalidChannelException, "The channel sent is invalid on a Raspberry Pi");
      return NULL;
   }

   if (get_function(channel) != OUTPUT)
   {
      PyErr_SetString(_InvalidDirectionException, "The GPIO channel has not been set up as an OUTPUT");
      return NULL;
   }

   output(channel, value);

   Py_INCREF(Py_None);
   return Py_None;
}

// python function output(channel, value)
static PyObject *py_output_sequence(PyObject *self, PyObject *args, PyObject *kwargs)
{
  int channel, period;
  char* sequence;
  static char *kwlist[] = {"channel", "period", "sequence", NULL};

  if (!PyArg_ParseTupleAndKeywords(args, kwargs, "iis", kwlist, &channel, &period, &sequence))
	 return NULL;

  if (channel < 0 || channel >= GPIO_COUNT)
  {
	 PyErr_SetString(_InvalidChannelException, "The channel sent is invalid on a Raspberry Pi");
	 return NULL;
  }

  if (get_function(channel) != OUTPUT)
  {
	 PyErr_SetString(_InvalidDirectionException, "The GPIO channel has not been set up as an OUTPUT");
	 return NULL;
  }

  outputSequence(channel, period, sequence);

  Py_INCREF(Py_None);
  return Py_None;
}


static PyObject *py_pulseMilli(PyObject *self, PyObject *args, PyObject *kwargs)
{
  int channel, up, down;
  static char *kwlist[] = {"channel", "up", "down", NULL};

  if (!PyArg_ParseTupleAndKeywords(args, kwargs, "iii", kwlist, &channel, &up, &down))
	 return NULL;

  if (channel < 0 || channel >= GPIO_COUNT)
  {
	 PyErr_SetString(_InvalidChannelException, "The channel sent is invalid on a Raspberry Pi");
	 return NULL;
  }

  if (get_function(channel) != OUTPUT)
  {
	 PyErr_SetString(_InvalidDirectionException, "The GPIO channel has not been set up as an OUTPUT");
	 return NULL;
  }

  pulseMilli(channel, up, down);

  Py_INCREF(Py_None);
  return Py_None;
}


static PyObject *py_pulseMilliRatio(PyObject *self, PyObject *args, PyObject *kwargs)
{
  int channel, width;
  float ratio;
  static char *kwlist[] = {"channel", "ratio", "width", NULL};

  if (!PyArg_ParseTupleAndKeywords(args, kwargs, "ifi", kwlist, &channel, &ratio, &width))
	 return NULL;

  if (channel < 0 || channel >= GPIO_COUNT)
  {
	 PyErr_SetString(_InvalidChannelException, "The channel sent is invalid on a Raspberry Pi");
	 return NULL;
  }

  if (get_function(channel) != OUTPUT)
  {
	 PyErr_SetString(_InvalidDirectionException, "The GPIO channel has not been set up as an OUTPUT");
	 return NULL;
  }

  pulseMilliRatio(channel, ratio, width);

  Py_INCREF(Py_None);
  return Py_None;
}


static PyObject *py_pulseMicro(PyObject *self, PyObject *args, PyObject *kwargs)
{
  int channel, up, down;
  static char *kwlist[] = {"channel", "up", "down", NULL};

  if (!PyArg_ParseTupleAndKeywords(args, kwargs, "iii", kwlist, &channel, &up, &down))
	 return NULL;

  if (channel < 0 || channel >= GPIO_COUNT)
  {
	 PyErr_SetString(_InvalidChannelException, "The channel sent is invalid on a Raspberry Pi");
	 return NULL;
  }

  if (get_function(channel) != OUTPUT)
  {
	 PyErr_SetString(_InvalidDirectionException, "The GPIO channel has not been set up as an OUTPUT");
	 return NULL;
  }

  pulseMicro(channel, up, down);

  Py_INCREF(Py_None);
  return Py_None;
}

static PyObject *py_pulseMicroRatio(PyObject *self, PyObject *args, PyObject *kwargs)
{
  int channel, width;
  float ratio;
  static char *kwlist[] = {"channel", "ratio", "width", NULL};

  if (!PyArg_ParseTupleAndKeywords(args, kwargs, "ifi", kwlist, &channel, &ratio, &width))
	 return NULL;

  if (channel < 0 || channel >= GPIO_COUNT)
  {
	 PyErr_SetString(_InvalidChannelException, "The channel sent is invalid on a Raspberry Pi");
	 return NULL;
  }

  if (get_function(channel) != OUTPUT)
  {
	 PyErr_SetString(_InvalidDirectionException, "The GPIO channel has not been set up as an OUTPUT");
	 return NULL;
  }

  pulseMicroRatio(channel, ratio, width);

  Py_INCREF(Py_None);
  return Py_None;
}

static PyObject *py_pulseAngle(PyObject *self, PyObject *args, PyObject *kwargs)
{
  int channel;
  float angle;
  static char *kwlist[] = {"channel", "angle", NULL};

  if (!PyArg_ParseTupleAndKeywords(args, kwargs, "if", kwlist, &channel, &angle))
	 return NULL;

  if (channel < 0 || channel >= GPIO_COUNT)
  {
	 PyErr_SetString(_InvalidChannelException, "The channel sent is invalid on a Raspberry Pi");
	 return NULL;
  }

  if (get_function(channel) != OUTPUT)
  {
	 PyErr_SetString(_InvalidDirectionException, "The GPIO channel has not been set up as an OUTPUT");
	 return NULL;
  }

  pulseAngle(channel, angle);

  Py_INCREF(Py_None);
  return Py_None;
}

static PyObject *py_pulseRatio(PyObject *self, PyObject *args, PyObject *kwargs)
{
  int channel;
  float ratio;
  static char *kwlist[] = {"channel", "ratio", NULL};

  if (!PyArg_ParseTupleAndKeywords(args, kwargs, "if", kwlist, &channel, &ratio))
	 return NULL;

  if (channel < 0 || channel >= GPIO_COUNT)
  {
	 PyErr_SetString(_InvalidChannelException, "The channel sent is invalid on a Raspberry Pi");
	 return NULL;
  }

  if (get_function(channel) != OUTPUT)
  {
	 PyErr_SetString(_InvalidDirectionException, "The GPIO channel has not been set up as an OUTPUT");
	 return NULL;
  }

  pulseRatio(channel, ratio);

  Py_INCREF(Py_None);
  return Py_None;
}

static PyObject *py_enableLoop(PyObject *self, PyObject *args)
{
   int channel;

   if (!PyArg_ParseTuple(args, "i", &channel))
      return NULL;

   enableLoop(channel);
   return Py_None;
}

static PyObject *py_disableLoop(PyObject *self, PyObject *args)
{
   int channel;

   if (!PyArg_ParseTuple(args, "i", &channel))
      return NULL;
   disableLoop(channel);
   return Py_None;
}



// python function value = input(channel)
static PyObject *py_input(PyObject *self, PyObject *args)
{
   int channel;

   if (!PyArg_ParseTuple(args, "i", &channel))
      return NULL;
   //   printf("Input GPIO %d\n", gpio);
   if (input(channel))
      Py_RETURN_TRUE;
   else
      Py_RETURN_FALSE;
}

// python function value = gpio_function(gpio)
static PyObject *py_get_function(PyObject *self, PyObject *args)
{
   int gpio, f;

   if (!PyArg_ParseTuple(args, "i", &gpio))
      return NULL;
      
   f = get_function(gpio);
   return Py_BuildValue("i", f);
}

// python function value = gpio_function(gpio)
static PyObject *py_get_function_string(PyObject *self, PyObject *args)
{
   int gpio, f;
   char *str;

   if (!PyArg_ParseTuple(args, "i", &gpio))
      return NULL;

   f = get_function(gpio);
   str = FUNCTIONS[f];
   return Py_BuildValue("s", str);
}

PyMethodDef python_methods[] = {
   {"getFunction", py_get_function, METH_VARARGS, "Return the current GPIO function (IN, OUT, ALT0)"},
   {"getFunctionString", py_get_function_string, METH_VARARGS, "Return the current GPIO function (IN, OUT, ALT0) as string"},
   {"setFunction", (PyCFunction)py_set_function, METH_VARARGS | METH_KEYWORDS, "Set up the GPIO channel,direction and (optional) pull/up down control\nchannel   - BCM GPIO number\ndirection - INPUT or OUTPUT\n[pull_up_down] - PUD_OFF (default), PUD_UP or PUD_DOWN"},
   {"input", py_input, METH_VARARGS, "Input from a GPIO channel"},
   {"output", (PyCFunction)py_output, METH_VARARGS | METH_KEYWORDS, "Output to a GPIO channel"},
   {"outputSequence", (PyCFunction)py_output_sequence, METH_VARARGS | METH_KEYWORDS, "Output a sequence to a GPIO channel"},
   {"pulseMilli", (PyCFunction)py_pulseMilli, METH_VARARGS | METH_KEYWORDS, "Output a single pulse to a GPIO channel"},
   {"pulseMilliRatio", (PyCFunction)py_pulseMilliRatio, METH_VARARGS | METH_KEYWORDS, "Output a single pulse to a GPIO channel"},
   {"pulseMicro", (PyCFunction)py_pulseMicro, METH_VARARGS | METH_KEYWORDS, "Output a single pulse to a GPIO channel"},
   {"pulseMicroRatio", (PyCFunction)py_pulseMicroRatio, METH_VARARGS | METH_KEYWORDS, "Output a single pulse to a GPIO channel"},
   {"pulseAngle", (PyCFunction)py_pulseAngle, METH_VARARGS | METH_KEYWORDS, "Output a single pulse to a GPIO channel"},
   {"pulseRatio", (PyCFunction)py_pulseRatio, METH_VARARGS | METH_KEYWORDS, "Output a single pulse to a GPIO channel"},
   {"enableLoop", py_enableLoop, METH_VARARGS, "Input from a GPIO channel"},
   {"disableLoop", py_disableLoop, METH_VARARGS, "Input from a GPIO channel"},
   {NULL, NULL, 0, NULL}
};

#if PY_MAJOR_VERSION > 2
static struct PyModuleDef python_module = {
   PyModuleDef_HEAD_INIT,
   "_webiopi.GPIO", /* name of module */
   NULL,       /* module documentation, may be NULL */
   -1,         /* size of per-interpreter state of the module,
                  or -1 if the module keeps state in global variables. */
   python_methods
};
#endif

#if PY_MAJOR_VERSION > 2
PyMODINIT_FUNC PyInit_GPIO(void)
#else
PyMODINIT_FUNC initGPIO(void)
#endif
{
   PyObject *module = NULL;
   int revision = -1;

#if PY_MAJOR_VERSION > 2
   if ((module = PyModule_Create(&python_module)) == NULL)
      goto exit;
#else
   if ((module = Py_InitModule("_webiopi.GPIO", python_methods)) == NULL)
      goto exit;
#endif

   _SetupException = PyErr_NewException("_webiopi.GPIO.SetupException", NULL, NULL);
   PyModule_AddObject(module, "SetupException", _SetupException);

   _InvalidDirectionException = PyErr_NewException("_webiopi.GPIO.InvalidDirectionException", NULL, NULL);
   PyModule_AddObject(module, "InvalidDirectionException", _InvalidDirectionException);

   _InvalidChannelException = PyErr_NewException("_webiopi.GPIO.InvalidChannelException", NULL, NULL);
   PyModule_AddObject(module, "InvalidChannelException", _InvalidChannelException);

   _InvalidPullException = PyErr_NewException("_webiopi.GPIO.InvalidPullException", NULL, NULL);
   PyModule_AddObject(module, "InvalidPullException", _InvalidPullException);

   _gpioCount = Py_BuildValue("i", GPIO_COUNT);
   PyModule_AddObject(module, "GPIO_COUNT", _gpioCount);

   _low = Py_BuildValue("i", LOW);
   PyModule_AddObject(module, "LOW", _low);

   _high = Py_BuildValue("i", HIGH);
   PyModule_AddObject(module, "HIGH", _high);

   _input = Py_BuildValue("i", INPUT);
   PyModule_AddObject(module, "IN", _input);
   
   _output = Py_BuildValue("i", OUTPUT);
   PyModule_AddObject(module, "OUT", _output);

   _alt0 = Py_BuildValue("i", ALT0);
   PyModule_AddObject(module, "ALT0", _alt0);

   _alt1 = Py_BuildValue("i", ALT1);
   PyModule_AddObject(module, "ALT0", _alt1);

   _alt2 = Py_BuildValue("i", ALT2);
   PyModule_AddObject(module, "ALT0", _alt2);

   _alt3 = Py_BuildValue("i", ALT3);
   PyModule_AddObject(module, "ALT0", _alt3);

   _alt4 = Py_BuildValue("i", ALT4);
   PyModule_AddObject(module, "ALT0", _alt4);

   _alt5 = Py_BuildValue("i", ALT5);
   PyModule_AddObject(module, "ALT0", _alt5);

   _pud_off = Py_BuildValue("i", PUD_OFF);
   PyModule_AddObject(module, "PUD_OFF", _pud_off);
   
   _pud_up = Py_BuildValue("i", PUD_UP);
   PyModule_AddObject(module, "PUD_UP", _pud_up);
   
   _pud_down = Py_BuildValue("i", PUD_DOWN);
   PyModule_AddObject(module, "PUD_DOWN", _pud_down);
      
   // detect board revision and set up accordingly
   revision = get_rpi_revision();
   if (revision == -1)
   {
      PyErr_SetString(_SetupException, "This module can only be run on a Raspberry Pi!");
#if PY_MAJOR_VERSION > 2
      return NULL;
#else
      return;
#endif
   }

   _board_revision = Py_BuildValue("i", revision);
   PyModule_AddObject(module, "BOARD_REVISION", _board_revision);
   
   // set up mmaped areas
   if (module_setup() != SETUP_OK )
   {
#if PY_MAJOR_VERSION > 2
      return NULL;
#else
      return;
#endif
   }
      
   if (Py_AtExit(cleanup) != 0)
   {
     cleanup();
#if PY_MAJOR_VERSION > 2
      return NULL;
#else
      return;
#endif
   }

exit:
#if PY_MAJOR_VERSION > 2
   return module;
#else
   return;
#endif
}
