# -*- coding: utf-8 -*-

import usb.core
import usb.util
from asq.initiators import query
from thermite.thermal_printer import ThermalPrinter

# See usb._lookup.interface_classes
INTERFACE_CLASS_PRINTER = 7


class UsbPrinter(ThermalPrinter):
    def __init__(self, vendor_id, product_id, in_ep, out_ep):
        ThermalPrinter.__init__(self)
        self.device = None
        self.printer_configuration = None
        self.printer_interface = None
        self.vendor_id = vendor_id
        self.product_id = product_id
        self.in_ep_id = in_ep
        self.out_ep_id = out_ep
        self.in_ep = None
        self.out_ep = None

    def connect(self):
        # Find USB device by id
        device = usb.core.find(idVendor=self.vendor_id,
                               idProduct=self.product_id)
        if device is None:
            raise ValueError('The device {0}:{1} is not connected'.format(
                self.vendor_id, self.product_id))

        # Device has been found, memorize
        self.device = device

        # Iterate over all interfaces of all configurations and try to find
        # the "printer" interface
        printer_configuration, printer_interface = self.get_printer_cfg_and_interface(
            device)

        # Device exposes valid configuration and interface, memorize
        self.printer_configuration = printer_configuration
        self.printer_interface = printer_interface

        # If the OS has a driver for the printer interface, we need to unload
        # it so we can talk to the device directly in raw mode
        if device.is_kernel_driver_active(printer_interface.bInterfaceNumber):
            device.detach_kernel_driver(printer_interface.bInterfaceNumber)

        # Activate the printer interface, this time without driver interference
        device.set_configuration(printer_configuration.bConfigurationValue)
        # Resetting the device re-enumerates the device
        device.reset()

        endpoints = dict((ep.bEndpointAddress, ep)
                         for ep in printer_interface.endpoints())

        self.in_ep = endpoints[self.in_ep_id]
        self.out_ep = endpoints[self.out_ep_id]

        return self

    @classmethod
    def get_printer_cfg_and_interface(cls, device):
        printer_configuration, printer_interface = query(device.configurations()).\
            select_many(lambda cfg: ((cfg, interface) for interface in cfg.interfaces())).\
            single(lambda cfg_interface: cfg_interface[1].bInterfaceClass == INTERFACE_CLASS_PRINTER)
        return printer_configuration, printer_interface

    @classmethod
    def sniff_devices(cls):
        for device in usb.core.find(find_all=True):
            try:
                printer_configuration, printer_interface = cls.get_printer_cfg_and_interface(
                    device)
                in_ep = query(printer_interface.endpoints()).single(
                    lambda ep: usb.util.endpoint_direction(ep.bEndpointAddress) == usb.util.ENDPOINT_IN)
                out_ep = query(printer_interface.endpoints()).single(
                    lambda ep: usb.util.endpoint_direction(ep.bEndpointAddress) == usb.util.ENDPOINT_OUT)
                yield UsbPrinter(device.idVendor, device.idProduct,
                                 in_ep.bEndpointAddress,
                                 out_ep.bEndpointAddress)
            except:
                continue

    def write(self, data, timeout_ms=None):
        self.out_ep.write(data, timeout=timeout_ms)
        return self

    def read(self, size, timeout_ms=None):
        new_data = self.in_ep.read(size, timeout=timeout_ms)
        self.append_read_buffer(new_data)
        return self.deflate_read_buffer()


if __name__=='__main__':
    p = query(UsbPrinter.sniff_devices()).single()
    #or set address manually:
    #p = UsbPrinter(0x0416, 0x5011, 0, 0)
    p.connect()
