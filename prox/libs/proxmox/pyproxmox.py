"""
A python wrapper for the Proxmox 2.x API.

Example usage:

1) Create an instance of the prox_auth class by passing in the
url or ip of a server, username and password:

a = prox_auth('vnode01.example.org','apiuser@pve','examplePassword')

2) Create and instance of the pyproxmox class using the auth object as a parameter:

b = pyproxmox(a)

3) Run the pre defined methods of the pyproxmox class. NOTE: they all return data, usually in JSON format:

status = b.getClusterStatus('vnode01')

For more information see https://github.com/Daemonthread/pyproxmox.
"""
import json
import requests

# Authentication class
class prox_auth:
    """
    The authentication class, requires three strings:
    
    1. An IP/resolvable url (minus the https://)
    2. Valid username, including the @pve or @pam
    3. A password
    
    Creates the required ticket and CSRF prevention token for future connections.
    
    Designed to be instanciated then passed to the new pyproxmox class as an init parameter.
    """
    def __init__(self,url,username,password):
        self.url = url
        self.connect_data = { "username":username, "password":password }
        self.full_url = "https://%s:8006/api2/json/access/ticket" % (self.url)

        self.response = requests.post(self.full_url,verify=False,data=self.connect_data)
    
        self.returned_data = self.response.json()
        
        self.ticket = {'PVEAuthCookie':self.returned_data['data']['ticket']}
        self.CSRF = self.returned_data['data']['CSRFPreventionToken']

# The meat and veg class
class pyproxmox:
    """
    A class that acts as a python wrapper for the Proxmox 2.x API.
    Requires a valid instance of the prox_auth class when initializing.
    
    GET and POST methods are currently implemented along with quite a few
    custom API methods.
    """
    # INIT
    def __init__(self, auth_class):
        """Take the prox_auth instance and extract the important stuff"""
        self.url = auth_class.url
        self.ticket = auth_class.ticket
        self.CSRF = auth_class.CSRF
    
    def connect(self, conn_type, option, post_data):
        """
        The main communication method.
        """
        self.full_url = "https://%s:8006/api2/json/%s" % (self.url,option)
    
        httpheaders = {'Accept':'application/json','Content-Type':'application/x-www-form-urlencoded'}

        if conn_type == "post":
            httpheaders['CSRFPreventionToken'] = str(self.CSRF)
            self.response = requests.post(self.full_url, verify=False, 
                                          data = post_data, 
                                          cookies = self.ticket,
                                          headers = httpheaders)

        elif conn_type == "put":
            httpheaders['CSRFPreventionToken'] = str(self.CSRF)
            self.response = requests.put(self.full_url, verify=False, 
                                          data = post_data, 
                                          cookies = self.ticket,
                                          headers = httpheaders)
        elif conn_type == "delete":
            httpheaders['CSRFPreventionToken'] = str(self.CSRF)
            self.response = requests.delete(self.full_url, verify=False, 
                                          data = post_data, 
                                          cookies = self.ticket,
                                          headers = httpheaders)
        elif conn_type == "get":
            self.response = requests.get (self.full_url, verify=False, 
                                          cookies = self.ticket)

        try:
            self.returned_data = self.response.json()
            return self.returned_data
        except:
            print("Error in trying to process JSON")
            print(self.response)


    """
    Methods using the GET protocol to communicate with the Proxmox API.
    """

    # Cluster Methods
    def getClusterStatus(self):
        """Get cluster status information. Returns JSON"""
        data = self.connect('get','cluster/status',None)
        return data

    def getClusterBackupSchedule(self):
        """List vzdump backup schedule. Returns JSON"""
        data = self.connect('get','cluster/backup',None)
        return data

    def getClusterVmNextId(self):
        """Get next VM ID of cluster. Returns JSON"""
        data = self.connect('get','cluster/nextid',None)
        return data


    # Node Methods
    def getVm(self):
        """Get cluster status information. Returns JSON"""
        data = self.connect('get','nodes/pve/qemu',None)
        return data

    def getNodeNetworks(self,node):
        """List available networks. Returns JSON"""
        data = self.connect('get','nodes/%s/network' % (node),None)
        return data

    def getNodeInterface(self,node,interface):
        """Read network device configuration. Returns JSON"""
        data = self.connect('get','nodes/%s/network/%s' % (node,interface),None)
        return data

    def getNodeContainerIndex(self,node):
        """OpenVZ container index (per node). Returns JSON"""
        data = self.connect('get','nodes/%s/openvz' % (node),None)
        return data

    def getNodeVirtualIndex(self,node):
        """Virtual machine index (per node). Returns JSON"""
        data = self.connect('get','nodes/%s/qemu' % (node),None)
        return data

    def getNodeServiceList(self,node):
        """Service list. Returns JSON"""
        data = self.connect('get','nodes/%s/services' % (node),None)
        return data

    def getNodeServiceState(self,node,service):
        """Read service properties"""
        data = self.connect('get','nodes/%s/services/%s/state' % (node,service),None)
        return data

    def getNodeStorage(self,node):
        """Get status for all datastores. Returns JSON"""
        data = self.connect('get','nodes/%s/storage' % (node),None)
        return data

    def getNodeFinishedTasks(self,node):
        """Read task list for one node (finished tasks). Returns JSON"""
        data = self.connect('get','nodes/%s/tasks' % (node),None)
        return data

    def getNodeDNS(self,node):
        """Read DNS settings. Returns JSON"""
        data = self.connect('get','nodes/%s/dns' % (node),None)
        return data

    def getNodeStatus(self,node):
        """Read node status. Returns JSON"""
        data = self.connect('get','nodes/%s/status' % (node),None)
        return data

    def getNodeSyslog(self,node):
        """Read system log. Returns JSON"""
        data = self.connect('get','nodes/%s/syslog' % (node),None)
        return data

    def getNodeRRD(self,node):
        """Read node RRD statistics. Returns PNG"""
        data = self.connect('get','nodes/%s/rrd' % (node),None)
        return data
    
    def getNodeRRDData(self,node):
        """Read node RRD statistics. Returns RRD"""
        data = self.connect('get','nodes/%s/rrddata' % (node),None)
        return data

    def getNodeBeans(self,node):
        """Get user_beancounters failcnt for all active containers. Returns JSON"""
        data = self.connect('get','nodes/%s/ubfailcnt' % (node),None)
        return data

    def getNodeTaskByUPID(self,node,upid):
        """Get tasks by UPID. Returns JSON"""
        data = self.connect('get','nodes/%s/tasks/%s' % (node,upid),None)
        return data

    def getNodeTaskLogByUPID(self,node,upid):
        """Read task log. Returns JSON"""
        data = self.connect('get','nodes/%s/tasks/%s/log' % (node,upid),None)
        return data

    def getNodeTaskStatusByUPID(self,node,upid):
        """Read task status. Returns JSON"""
        data = self.connect('get','nodes/%s/tasks/%s/status' % (node,upid),None)
        return data

    # Scan

    def getNodeScanMethods(self,node):
        """Get index of available scan methods"""
        data = self.connect('get','nodes/%s/scan' % (node),None)
        return data

    def getRemoteiSCSI(self,node):
        """Scan remote iSCSI server."""
        data = self.connect('get','nodes/%s/scan/iscsi' % (node),None)
        return data

    def getNodeLVMGroups(self,node):
        """Scan local LVM groups"""
        data = self.connect('get','nodes/%s/scan/lvm' % (node),None)
        return data

    def getRemoteNFS(self,node):
        """Scan remote NFS server"""
        data = self.connect('get','nodes/%s/scan/nfs' % (node),None)
        return data

    def getNodeUSB(self,node):
        """List local USB devices"""
        data = self.connect('get','nodes/%s/scan/usb' % (node),None)
        return data


    
    # OpenVZ Methods

    def getContainerIndex(self,node,vmid):
        """Directory index. Returns JSON"""
        data = self.connect('get','nodes/%s/openvz/%s' % (node,vmid),None)
        return data

    def getContainerStatus(self,node,vmid):
        """Get virtual machine status. Returns JSON"""
        data = self.connect('get','nodes/%s/openvz/%s/status/current' % (node,vmid),None)
        return data

    def getContainerBeans(self,node,vmid):
        """Get container user_beancounters. Returns JSON"""
        data = self.connect('get','nodes/%s/openvz/%s/status/ubc' % (node,vmid),None)
        return data

    def getContainerConfig(self,node,vmid):
        """Get container configuration. Returns JSON"""
        data = self.connect('get','nodes/%s/openvz/%s/config' % (node,vmid),None)
        return data

    def getContainerInitLog(self,node,vmid):
        """Read init log. Returns JSON"""
        data = self.connect('get','nodes/%s/openvz/%s/initlog' % (node,vmid),None)
        return data

    def getContainerRRD(self,node,vmid):
        """Read VM RRD statistics. Returns PNG"""
        data = self.connect('get','nodes/%s/openvz/%s/rrd' % (node,vmid),None)
        return data

    def getContainerRRDData(self,node,vmid):
        """Read VM RRD statistics. Returns RRD"""
        data = self.connect('get','nodes/%s/openvz/%s/rrddata' % (node,vmid),None)
        return data

    # KVM Methods

    def getVirtualIndex(self,node,vmid):
        """Directory index. Returns JSON"""
        data = self.connect('get','nodes/%s/qemu/%s' % (node,vmid),None)
        return data

    def getVirtualStatus(self,node,vmid):
        """Get virtual machine status. Returns JSON"""
        data = self.connect('get','nodes/%s/qemu/%s/status/current' % (node,vmid),None)
        return data

    def getVirtualInfo(self,node,vmid, action):
        """Get virtual info configuration. Returns JSON"""
        data = self.connect('get','nodes/%s/qemu/%s/%s' % (node,vmid, action),None)
        return data

    def getVirtualConfig(self,node,vmid):
        """Get virtual machine configuration. Returns JSON"""
        data = self.connect('get','nodes/%s/qemu/%s/config' % (node,vmid),None)
        return data

    def getVirtualRRD(self,node,vmid):
        """Read VM RRD statistics. Returns JSON"""
        data = self.connect('get','nodes/%s/qemu/%s/rrd' % (node,vmid),None)
        return data

    def getVirtualRRDData(self,node,vmid):
        """Read VM RRD statistics. Returns JSON"""
        data = self.connect('get','nodes/%s/qemu/%s/rrddata' % (node,vmid),None)
        return data

    # Storage Methods

    def getStorageVolumeData(self,node,storage,volume):
        """Get volume attributes. Returns JSON"""
        data = self.connect('get','nodes/%s/storage/%s/content/%s' % (node,storage,volume),None)
        # data = self.connect('get','nodes/%s/storage/%s/content/' % (node,storage),None)
        return data

    def getStorageConfig(self,storage):
        """Read storage config. Returns JSON"""
        data = self.connect('get','storage/%s' % (storage),None)
        return data
    
    def getNodeStorageContent(self,node,storage):
        """List storage content. Returns JSON"""
        data = self.connect('get','nodes/%s/storage/%s/content' % (node,storage),None)
        return data

    def getNodeStorageRRD(self,node,storage):
        """Read storage RRD statistics. Returns JSON"""
        data = self.connect('get','nodes/%s/storage/%s/rrd' % (node,storage),None)
        return data

    def getNodeStorageRRDData(self,node,storage):
        """Read storage RRD statistics. Returns JSON"""
        data = self.connect('get','nodes/%s/storage/%s/rrddata' % (node,storage),None)
        return data

    """
    Methods using the POST protocol to communicate with the Proxmox API. 
    """
    
    # OpenVZ Methods
    
    def createOpenvzContainer(self,node,post_data):
        """
        Create or restore a container. Returns JSON
        Requires a dictionary of tuples formatted [('postname1','data'),('postname2','data')]
        """
        data = self.connect('post','nodes/%s/openvz' % (node), post_data)
        return data

    def mountOpenvzPrivate(self,node,vmid):
        """Mounts container private area. Returns JSON"""
        post_data = None
        data = self.connect('post','nodes/%s/openvz/%s/status/mount' % (node,vmid), post_data)
        return data

    def shutdownOpenvzContainer(self,node,vmid):
        """Shutdown the container. Returns JSON"""
        post_data = None
        data = self.connect('post','nodes/%s/openvz/%s/status/shutdown' % (node,vmid), post_data)
        return data

    def startOpenvzContainer(self,node,vmid):
        """Start the container. Returns JSON"""
        post_data = None
        data = self.connect('post','nodes/%s/openvz/%s/status/start' % (node,vmid), post_data)
        return data

    def stopOpenvzContainer(self,node,vmid):
        """Stop the container. Returns JSON"""
        post_data = None
        data = self.connect('post','nodes/%s/openvz/%s/status/stop' % (node,vmid), post_data)
        return data

    def unmountOpenvzPrivate(self,node,vmid):
        """Unmounts container private area. Returns JSON"""
        post_data = None
        data = self.connect('post','nodes/%s/openvz/%s/status/unmount' % (node,vmid), post_data)
        return data

    def migrateOpenvzContainer(self,node,vmid,target):
        """Migrate the container to another node. Creates a new migration task. Returns JSON"""
        post_data = {'target': str(target)}
        data = self.connect('post','nodes/%s/openvz/%s/migrate' % (node,vmid), post_data)
        return data

    # KVM Methods

    def createVirtualMachine(self,node,post_data):
        """
        Create or restore a virtual machine. Returns JSON
        """
        data = self.connect('post',"nodes/%s/qemu" % (node), post_data)
        return data
        
    def resetVirtualMachine(self,node,vmid):
        """Reset a virtual machine. Returns JSON"""
        post_data = None
        data = self.connect('post',"nodes/%s/qemu/%s/status/reset" % (node,vmid), post_data)
        return data
        
    def resumeVirtualMachine(self,node,vmid):
        """Resume a virtual machine. Returns JSON"""
        post_data = None
        data = self.connect('post',"nodes/%s/qemu/%s/status/resume" % (node,vmid), post_data)
        return data
        
    def shutdownVirtualMachine(self,node,vmid):
        """Shut down a virtual machine. Returns JSON"""
        post_data = None
        data = self.connect('post',"nodes/%s/qemu/%s/status/shutdown" % (node,vmid), post_data)
        return data
    
    def startVirtualMachine(self,node,vmid):
        """Start a virtual machine. Returns JSON"""
        post_data = None
        data = self.connect('post',"nodes/%s/qemu/%s/status/start" % (node,vmid), post_data)
        return data
        
    def stopVirtualMachine(self,node,vmid):
        """Stop a virtual machine. Returns JSON"""
        post_data = None
        data = self.connect('post',"nodes/%s/qemu/%s/status/stop" % (node,vmid), post_data)
        return data

    def suspendVirtualMachine(self,node,vmid):
        """Suspend a virtual machine. Returns JSON"""
        post_data = None
        data = self.connect('post',"nodes/%s/qemu/%s/status/suspend" % (node,vmid), post_data)
        return data
        
    def migrateVirtualMachine(self,node,vmid,target):
        """Migrate a virtual machine. Returns JSON"""
        post_data = {'target': str(target)}
        data = self.connect('post',"nodes/%s/qemu/%s/status/start" % (node,vmid), post_data)
        return data

    def monitorVirtualMachine(self,node,vmid,command):
        """Send monitor command to a virtual machine. Returns JSON"""
        post_data = {'command': str(command)}
        data = self.connect('post',"nodes/%s/qemu/%s/monitor" % (node,vmid), post_data)
        return data
        
    def vncproxyVirtualMachine(self,node,vmid):
        """Creates a VNC Proxy for a virtual machine. Returns JSON"""
        post_data = None
        data = self.connect('post',"nodes/%s/qemu/%s/vncproxy" % (node,vmid), post_data)
        return data

    def rollbackVirtualMachine(self,node,vmid,snapname):
        """Rollback a snapshot of a virtual machine. Returns JSON"""
        post_data = None
        data = self.connect('post',"nodes/%s/qemu/%s/snapshot/%s/rollback" % (node,vmid,snapname), post_data)
        return data
    
    def getSnapshotConfigVirtualMachine(self,node,vmid,snapname):
        """Get snapshot config of a virtual machine. Returns JSON"""
        post_data = None
        data = self.connect('get',"nodes/%s/qemu/%s/snapshot/%s/config" % (node,vmid,snapname), post_data)
        return data

        
    """
    Methods using the DELETE protocol to communicate with the Proxmox API. 
    """
    
    # OPENVZ
    
    def deleteOpenvzContainer(self,node,vmid):
        """Deletes the specified openvz container"""
        data = self.connect('delete',"nodes/%s/openvz/%s" % (node,vmid),None)
        return data

    # NODE
    
    def deleteNodeNetworkConfig(self,node):
        """Revert network configuration changes."""
        data = self.connect('delete',"nodes/%s/network" % (node),None)
        return data
    
    def deleteNodeInterface(self,node,interface):
        """Delete network device configuration"""
        data = self.connect('delete',"nodes/%s/network/%s" % (node,interface),None)
        return data
    
    #KVM
    
    def deleteVirtualMachine(self,node,vmid):
        """Destroy the vm (also delete all used/owned volumes)."""
        data = self.connect('delete',"nodes/%s/qemu/%s" % (node,vmid),None)
        return data
        
    # POOLS
    def deletePool(self,poolid):
        """Delete Pool"""
        data = self.connect('delete',"pools/%s" % (poolid),None)
        return data

    # STORAGE
    def deleteStorageConfiguration(self,storageid):
        """Delete storage configuration"""
        data = self.connect('delete',"storage/%s" % (storageid),None)
        return data

    """
    Methods using the PUT protocol to communicate with the Proxmox API. 
    """

    # NODE
    def setNodeDNSDomain(self,node,domain):
        """Set the nodes DNS search domain"""
        post_data = {'search': str(domain)}
        data = self.connect('put',"nodes/%s/dns" % (node), post_data)
        return data

    def setNodeSubscriptionKey(self,node,key):
        """Set the nodes subscription key"""
        post_data = {'key': str(key)}
        data = self.connect('put',"nodes/%s/subscription" % (node), post_data)
        return data
        
    def setNodeTimeZone(self,node,timezone):
        """Set the nodes timezone"""
        post_data = {'timezone': str(timezone)}
        data = self.connect('put',"nodes/%s/time" % (node), post_data)
        return data

    # OPENVZ
    def setOpenvzContainerOptions(self,node,vmid,post_data):
        """Set openvz virtual machine options."""
        data = self.connect('put',"nodes/%s/openvz/%s/config" % (node,vmid), post_data)
        return data
    
    # KVM
    def setVirtualMachineOptions(self,node,vmid,post_data):
        """Set KVM virtual machine options."""
        data = self.connect('put',"nodes/%s/qemu/%s/config" % (node,vmid), post_data)
        return data

    def sendKeyEventVirtualMachine(self,node,vmid, key):
        """Send key event to virtual machine"""
        post_data = {'key': str(key)}
        data = self.connect('put',"nodes/%s/qemu/%s/sendkey" % (node,vmid), post_data)
        return data

    def unlinkVirtualMachineDiskImage(self,node,vmid, post_data):
        """Unlink disk images"""
        data = self.connect('put',"nodes/%s/qemu/%s/unlink" % (node,vmid), post_data)
        return data

    # POOLS
    def setPoolData(self,poolid, post_data):
        """Update pool data."""
        data = self.connect('put',"pools/%s" % (poolid), post_data)
        return data

    # STORAGE
    def updateStorageConfiguration(self,storageid,post_data):
        """Update storage configuration"""
        data = self.connect('put',"storage/%s" % (storageid), post_data)
        return data

        
