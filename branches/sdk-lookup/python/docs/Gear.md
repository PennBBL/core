# Gear

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**author** | **str** | The author of this gear. | 
**maintainer** | **str** | (optional) The maintainer of this gear. Can be used to distinguish the algorithm author from the gear maintainer. | [optional] 
**cite** | **str** | (optional) Any citations relevant to the algorithm(s) or work present in the gear. | [optional] 
**config** | [**GearConfig**](GearConfig.md) |  | 
**custom** | [**GearCustom**](GearCustom.md) |  | [optional] 
**description** | **str** | A brief description of the gear&#39;s purpose. Ideally 1-4 sentences. | 
**environment** | [**GearEnvironment**](GearEnvironment.md) |  | [optional] 
**command** | **str** | If provided, the starting command for the gear, rather than /flywheel/v0/run. Will be templated according to the spec. | [optional] 
**inputs** | [**GearInputs**](GearInputs.md) |  | 
**label** | **str** | The human-friendly name of this gear. | 
**license** | **str** | Software license of the gear | 
**name** | **str** | The identification of this gear. | 
**source** | **str** | A valid URI, or empty string. | 
**url** | **str** | A valid URI, or empty string. | 
**version** | **str** | A human-friendly string explaining the release version of this gear. Example: 3.2.1 | 

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


